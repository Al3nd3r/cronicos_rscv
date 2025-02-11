from flask import Flask, redirect, url_for, render_template, request, flash, session, jsonify, make_response, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from functools import wraps
import random, string, os
import mysql.connector
import MySQLdb
import email
import html
from datetime import timedelta
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
import mysql.connector

app = Flask(__name__)
app.secret_key = '12345'

# CONFIGURACION DEL TIEMPO DE ESPERA EN PANTALLA
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

load_dotenv()

# CONEXION A MYSQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS')
mysql = MySQL(app)

# CONEXION PARA ENVIAR GMAIL
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)

# OBTENER EL NOMBRE DEL REMITENTE
sender_name = os.getenv('SENDER_NAME')

def no_cache(view):
    @wraps(view)
    def no_cache_wrapper(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache_wrapper

@app.route('/')
def ingresar():
    return render_template('iniciar_sesion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = html.escape(request.form.get('email', ''))
    password = html.escape(request.form.get('password', ''))

    # VALIDAR DATOS DE INGRESO
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT email, password FROM tabla_cronicos WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    if usuario and check_password_hash(usuario['password'], password):
        session['email'] = email
        flash('Inicio de sesión exitoso', 'login_success')
        return redirect(url_for('menu'))
    else:
        flash('Correo electrónico o contraseña incorrectos', 'login_error')
        return redirect(url_for('ingresar'))


@app.route('/menu')
def menu():
    if 'email' in session:
        return render_template('menu.html')
    else:
        return redirect(url_for('ingresar'))

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/correo')
def correo():
    return render_template('correo_electronico.html')

@app.route('/verificar')
def verificar():
    return render_template('verificar_codigo.html')


@app.route('/procesar_afiliado', methods=['POST'])
def procesar_afiliado():
    cedula = html.escape(request.form['cedula'])
    nomb = html.escape(request.form['nomb'])
    apell = html.escape(request.form['apell'])
    f_naci = html.escape(request.form['f_naci'])
    sex = html.escape(request.form['sex'])
    socio = html.escape(request.form['socio'])
    carnet = html.escape(request.form['carnet'])
    correo = html.escape(request.form['correo'])
    t_soli = html.escape(request.form['t_soli'])
    edo = html.escape(request.form['edo'])
    direc = html.escape(request.form['direc'])

    # Guardar en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO tabla_afiliado (cedula, nomb, apell, f_naci, sex, socio, carnet, correo, t_soli, edo, direc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                   (cedula, nomb, apell, f_naci, sex, socio, carnet, correo, t_soli, edo, direc))
    mysql.connection.commit()  # Asegúrate de hacer commit a la transacción
    cursor.close()

    # Flash message
    flash('Afiliado registrado exitosamente', 'register_success')
    
    return redirect(url_for('cronicos'))  # Cambia 'nombre_de_la_vista' por la vista a la que quieras redirigir

  




@app.route('/procesar', methods=['POST'])
def procesar():
    nombre = html.escape(request.form['nombre'])
    email = html.escape(request.form['email'])
    empresa = html.escape(request.form['empresa'])
    d_empresa = html.escape(request.form['d_empresa'])
    c_empresa = html.escape(request.form['c_empresa'])
    sede = html.escape(request.form['sede'])
    d_sede = html.escape(request.form['d_sede'])
    c_sede = html.escape(request.form['c_sede'])
    password = html.escape(request.form['password'])
    c_password = html.escape(request.form['c_password'])
    c_i = html.escape(request.form['c_i'])
    if password == c_password:
        hashed_password = generate_password_hash(password)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO tabla_cronicos (nombre, email, c_i, empresa, d_empresa, c_empresa, sede, d_sede, c_sede, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (nombre, email, c_i, empresa, d_empresa, c_empresa, sede, d_sede, c_sede, hashed_password))
        mysql.connection.commit()
        cursor.close()
        flash('Usuario registrado exitosamente', 'register_success')
        return redirect(url_for('ingresar'))
    else:
        flash("Las contraseñas no coinciden, inténtelo de nuevo", "register_error")
        return redirect(url_for('registro'))

@app.route('/error')
def error():
    flash("Se produjo un error.", "error")

def generate_random_code():
    return ''.join(random.choices(string.digits, k=6))

def send_email(remitente, destinatario, mensaje):
    email = EmailMessage()
    email['From'] = remitente
    email['To'] = destinatario
    email['Subject'] = 'Código'
    email.set_content(mensaje, charset='utf-8')

    smtp = smtplib.SMTP_SSL('smtp.gmail.com')
    smtp.login(remitente, 'eisb qwyu hgnx ylcz')
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()

@app.route('/correo_electronico', methods=['GET', 'POST'])
def correo_electronico():
    if request.method == 'POST':
        remitente = 'alenderg26@gmail.com'
        destinatario = request.form['email']
        codigo = generate_random_code()
        session['codigo'] = codigo
        send_email(remitente, destinatario, codigo)
        flash('El código ha sido enviado.')
        return redirect(url_for('verificar_codigo'))
    return render_template('correo_electronico.html')

@app.route('/enviar_correo', methods=['GET', 'POST'])
def enviar_correo():
    if request.method == 'POST':
        email = request.form['email']
        # Verificar si el correo electrónico está registrado
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT email FROM tabla_cronicos WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        
        if usuario:
            # Genera un código aleatorio compuesto solo por números (6 dígitos)
            codigo = ''.join(random.choices(string.digits, k=6))
            # Envía el correo con el código
            msg = Message('Código de Verificación', recipients=[email])
            msg.body = f'Tu código de verificación es: {codigo}'
            try:
                mail.send(msg)
                flash('Se ha enviado un código de verificación a tu correo.', 'info')
                # Guarda el código en la sesión
                session['codigo_verificacion'] = codigo
                session['email_verificacion'] = email
            except smtplib.SMTPAuthenticationError:
                print("Error de autenticación al enviar correo")
                flash('Error de autenticación al enviar el correo. Por favor, verifica tus credenciales y la configuración de seguridad de tu cuenta.', 'error')
            except smtplib.SMTPException as e:
                print(f"Error al enviar correo: {e}")
                flash(f'Error al enviar el correo: {e}', 'error')
            return redirect(url_for('verificar'))
        else:
            flash('Correo electrónico no registrado.', 'error')
            return render_template('correo_electronico.html', show_register_button=True)
    return render_template('correo_electronico.html')


@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if request.method == 'POST':
        codigo_ingresado = ''.join(request.form.getlist('codigo'))
        if codigo_ingresado == session.get('codigo_verificacion'):
            return redirect(url_for('cambiar_c'))
        else:
            flash('El código ingresado es incorrecto.', 'error')
    return render_template('verificar_codigo.html')

@app.route('/cambiar_c', methods=['GET', 'POST'])
def cambiar_c():
    if request.method == 'POST':
        nueva_contrasena = html.escape(request.form['nueva_contrasena'])
        confirmacion_contrasena = html.escape(request.form['confirmacion_contrasena'])

        if nueva_contrasena == confirmacion_contrasena:
            hashed_password = generate_password_hash(nueva_contrasena)
            email_usuario = session.get('email_verificacion')

            # Actualizar la contraseña en la base de datos
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE tabla_cronicos SET password = %s WHERE email = %s", (hashed_password, email_usuario))
            mysql.connection.commit()
            cursor.close()

            flash('Contraseña actualizada exitosamente', 'success')
            return redirect(url_for('ingresar'))
        else:
            flash('Las contraseñas no coinciden. Inténtalo de nuevo.', 'error')

    return render_template('cambiar_contrasena.html')

@app.route('/cronicos')
def cronicos():
    return render_template('afiliados.html')

@app.route('/entregas')
def entregas():
    return render_template('entregas.html')

@app.route('/consulta_recipes')
def consulta_recipes():
    return render_template('consulta_recipes.html')

@app.route('/consulta_informes')
def consulta_informes():
    return render_template('consulta_informes.html')

@app.route('/consulta_informes_suspendidos')
def consulta_informes_suspendidos():
    return render_template('consulta_informes_suspendidos.html')

@app.route('/listado')
def listado():
    return render_template('listado.html')

@app.route('/medicos')
def medicos():
    return render_template('medicos.html')

@app.route('/prestadores_clinicas')
def prestadores_clinicas():
    return render_template('prestadores_clinicas.html')

@app.route('/soporte')
def soporte():
    return render_template('soporte.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    return ('iniciar_sesion.html')

if __name__ == '__main__':
    app.run(debug=True)
