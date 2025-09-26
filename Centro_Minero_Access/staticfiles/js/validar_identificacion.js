document.addEventListener('DOMContentLoaded', function() {
    // Referencias a los elementos del formulario
    const tipoIdentificacion = document.getElementById('id_tipo_identificacion');
    const numeroIdentificacion = document.getElementById('id_numero_identificacion');
    const form = numeroIdentificacion.closest('form');
    
    // Contenedor para el mensaje de advertencia
    const warningDiv = document.createElement('div');
    warningDiv.className = 'alert alert-warning mt-2';
    warningDiv.style.display = 'none';
    
    // Inserta la advertencia justo después del campo de número de identificación
    numeroIdentificacion.parentNode.insertBefore(warningDiv, numeroIdentificacion.nextSibling);

    // Mapeo de tipos de identificación a sus longitudes
    // Puedes ajustar estos valores según los requisitos reales de tu institución
    const longitudes = {
        'cc': 10,  // Cédula de Ciudadanía (Colombia)
        'ti': 10,  // Tarjeta de Identidad (Colombia)
        'ce': 12,  // Cédula de Extranjería (ejemplo)
        'pa': 12,  // Pasaporte (ejemplo)
    };

    function validarNumero() {
        // Obtenemos el tipo de documento y el valor ingresado
        const tipoSeleccionado = tipoIdentificacion.value;
        const valorNumero = numeroIdentificacion.value;
        const longitudEsperada = longitudes[tipoSeleccionado];

        // 1. Validar que solo sean números si el tipo es CC o TI
        if (tipoSeleccionado === 'cc' || tipoSeleccionado === 'ti') {
            numeroIdentificacion.value = valorNumero.replace(/\D/g, '');
        }

        // 2. Validar la longitud
        if (valorNumero.length !== longitudEsperada) {
            warningDiv.textContent = `⛔ El número de ${tipoIdentificacion.options[tipoIdentificacion.selectedIndex].text} debe tener exactamente ${longitudEsperada} dígitos.`;
            warningDiv.style.display = 'block';
        } else {
            warningDiv.style.display = 'none';
        }
    }

    // Eventos para disparar la validación
    tipoIdentificacion.addEventListener('change', validarNumero);
    numeroIdentificacion.addEventListener('input', validarNumero);
});