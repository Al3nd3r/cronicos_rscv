var ver = document.getElementById('ver');
var input = document.getElementById('n_contrasena');
ver.addEventListener("click", function(){
    if(input.type =="password"){
        input.type = "text"
        ver.classList.add('ver-visible');
        }
        else{
            input.type = "password"
            ver.classList.remove('ver-visible');
        }
})

var ver2 = document.getElementById('ver2');
var input2 = document.getElementById('c_contrasena');
ver2.addEventListener("click", function(){
    if(input2.type =="password"){
        input2.type = "text"
        ver2.classList.add('ver-visible');
        }
        else{
            input2.type = "password"
            ver2.classList.remove('ver-visible');
        }
})