// FUNCION PARA ABRIR EL DESPLEGUE
const toggleDropdown = (dropdown, menu) => {
    if (dropdown.classList.contains('open')) {
        menu.style.height = '';
        dropdown.classList.remove('open');
    } else {
        menu.style.height = `${menu.scrollHeight}px`;
        dropdown.classList.add('open'); 
    }
}

// FUNCION PARA CERRAR LOS DESPLEGUES
const closeAllDropdowns = () => {
    document.querySelectorAll('.dropdown-container.open').forEach(openDropdown => {
        const menu = openDropdown.querySelector('.dropdown-menu');
        if (menu) {
            menu.style.height = ''; 
            openDropdown.classList.remove('open'); 
        }
    });
}

// Agregar evento a los elementos con la clase "dropdown-toggle"
document.querySelectorAll(".dropdown-toggle").forEach(dropdownToggle => {
    dropdownToggle.addEventListener("click", e => {
        e.preventDefault();

        const dropdown = e.target.closest(".dropdown-container");
        const menu = dropdown.querySelector(".dropdown-menu");

        if (dropdown && menu) {
            if (!dropdown.classList.contains('open')) {
                closeAllDropdowns();
            }
            toggleDropdown(dropdown, menu);
        } else {
            console.error("No se pudo encontrar el contenedor o el menú desplegable.");
        }
    });
});

// Evento para alternar la visibilidad de la barra lateral
document.querySelector(".sidebar-toggler").addEventListener("click", () => {
    document.querySelector(".sidebar").classList.toggle("collapsed");
});



