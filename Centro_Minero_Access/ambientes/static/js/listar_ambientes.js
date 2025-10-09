document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modal-deshabilitar');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('modalCancelBtn');
    const ambienteNombreSpan = document.getElementById('ambiente-nombre');
    const formDeshabilitar = document.getElementById('form-deshabilitar');

    // 📦 URL base desde el HTML oculto
    const baseUrl = document
        .getElementById('urlPatterns')
        .getAttribute('data-deshabilitar-url')
        .replace(/0\/?$/, ''); // elimina el "0" final

    // === ABRIR MODAL ===
    function openModal(nombreAmbiente, ambienteId) {
        ambienteNombreSpan.textContent = nombreAmbiente;
        formDeshabilitar.action = `${baseUrl}${ambienteId}/`;
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        modal.focus();
        document.body.style.overflow = 'hidden';
    }

    // === CERRAR MODAL ===
    function closeModal() {
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    // === EVENTOS DE CIERRE ===
    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModal();
        }
    });

    // === BOTONES DE DESHABILITAR ===
    const disableButtons = document.querySelectorAll('.btn-disable');

    disableButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const ambienteId = button.getAttribute('data-id');
            const nombreAmbiente = button.getAttribute('data-nombre');
            openModal(nombreAmbiente, ambienteId);
        });
    });

    // === OPCIONAL: cerrar modal tras submit ===
    formDeshabilitar.addEventListener('submit', () => {
        closeModal();
    });
});
