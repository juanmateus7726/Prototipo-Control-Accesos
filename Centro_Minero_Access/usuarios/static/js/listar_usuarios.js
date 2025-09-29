// =============================
// PANEL DE CONFIGURACIÓN
// =============================
const configLink = document.getElementById('configLink');
const configPanel = document.getElementById('configPanel');
const configOverlay = document.getElementById('configOverlay');
const closeConfig = document.getElementById('closeConfig');
const cancelConfig = document.getElementById('cancelConfig');
const saveConfig = document.getElementById('saveConfig');
const configMessage = document.getElementById('configMessage');

if (configLink && configPanel && configOverlay) {
    // Abrir panel
    configLink.addEventListener('click', (e) => {
        e.preventDefault();
        configPanel.classList.add('active');
        configOverlay.classList.add('active');
    });

    // Cerrar panel
    const closePanel = () => {
        configPanel.classList.remove('active');
        configOverlay.classList.remove('active');
    };

    if (closeConfig) closeConfig.addEventListener('click', closePanel);
    if (cancelConfig) cancelConfig.addEventListener('click', closePanel);
    configOverlay.addEventListener('click', closePanel);

    // Guardar configuración (simulado)
    if (saveConfig) {
        saveConfig.addEventListener('click', () => {
            configMessage.textContent = '✅ Configuración guardada correctamente.';
            setTimeout(() => { configMessage.textContent = ''; }, 3000);
            closePanel();
        });
    }
}

// =============================
// MODAL DESHABILITAR USUARIO
// =============================
const modal = document.getElementById('modal-deshabilitar');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelModalBtn = document.getElementById('modalCancelBtn');
const formDeshabilitar = document.getElementById('form-deshabilitar');
const usuarioNombreSpan = document.getElementById('usuario-nombre');

const disableBtns = document.querySelectorAll('.btn-disable');

const urlPatterns = document.getElementById('urlPatterns');
let urlBase = urlPatterns ? urlPatterns.dataset.deshabilitarUrl : null;

disableBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const nombre = btn.dataset.nombre;

        usuarioNombreSpan.textContent = nombre;
        if (urlBase) {
            formDeshabilitar.action = urlBase.replace('0', id);
        } else {
            formDeshabilitar.action = `/usuarios/deshabilitar/${id}/`;
        }

        modal.classList.add('show');
    });
});

const closeModal = () => modal.classList.remove('show');
if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
if (cancelModalBtn) cancelModalBtn.addEventListener('click', closeModal);
