document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modal-deshabilitar');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('modalCancelBtn');
    const ambienteNombreSpan = document.getElementById('ambiente-nombre');
    const formDeshabilitar = document.getElementById('form-deshabilitar');

    // Función para abrir el modal con datos dinámicos
    function openModal(nombreAmbiente, urlAction) {
        ambienteNombreSpan.textContent = nombreAmbiente;
        formDeshabilitar.action = urlAction;
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        modal.focus();
        document.body.style.overflow = 'hidden'; // Evitar scroll en background
    }

    // Función para cerrar el modal
    function closeModal() {
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = ''; // Restaurar scroll
    }

    // Cerrar modal con botón cerrar
    closeModalBtn.addEventListener('click', closeModal);

    // Cerrar modal con botón cancelar
    cancelBtn.addEventListener('click', closeModal);

    // Cerrar modal al hacer click fuera del contenido
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Cerrar modal con tecla ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModal();
        }
    });

    // Seleccionamos todos los botones "Deshabilitar" con clase .btn-disable
    const disableButtons = document.querySelectorAll('.btn-disable');

    disableButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault(); // Prevenir submit inmediato

            // Obtener el nombre del ambiente (primer td de la fila)
            const row = button.closest('tr');
            const nombreAmbiente = row.querySelector('td:first-child').textContent.trim();

            // Obtener la URL del formulario padre
            const form = button.closest('form');
            const urlAction = form.action;

            // Abrir modal con datos dinámicos
            openModal(nombreAmbiente, urlAction);
        });
    });

    // Opcional: cerrar modal al enviar formulario
    formDeshabilitar.addEventListener('submit', () => {
        closeModal();
    });
});
