document.addEventListener('DOMContentLoaded', function () {
    // =========================
    // PANEL DE CONFIGURACIÓN
    // =========================
    const configLink = document.getElementById('configLink');
    const configPanel = document.getElementById('configPanel');
    const cancelConfigBtn = document.getElementById('cancelConfig');
    const saveConfigBtn = document.getElementById('saveConfig');
    const configOverlay = document.getElementById('configOverlay');
    const configMessage = document.getElementById('configMessage');

    const themeSelect = document.getElementById('theme');
    const notificationsSelect = document.getElementById('notifications');
    const languageSelect = document.getElementById('language');
    const resultsInput = document.getElementById('resultsPerPage');

    const translations = {
        es: {
            pageTitle: '👥 Lista de Usuarios',
            createBtn: '+ Crear Usuario',
            thNombre: 'Nombre',
            thTipoIdentificacion: 'Tipo de Identificación',
            thNumeroIdentificacion: 'Número de Identificación',
            thTipo: 'Tipo',
            thEstado: 'Estado',
            thAcciones: 'Acciones',
            emptyStateText: 'No hay usuarios registrados en el sistema.',
            actionEdit: 'Editar',
            actionDisable: 'Deshabilitar',
            actionReactivate: 'Reactivar',
            footerMainText: 'Lista Central Sistema - SENA',
            footerSubtext: 'Arte digital sostenible',
            footerCopyright: '© 2024 Sistema de Control de Usuarios. Todos los derechos reservados.',
            message: '¡Configuración guardada!',
            confirmDisableTitle: '¿Deshabilitar Usuario?',
            confirmDisableText: '¿Seguro que deseas deshabilitar este usuario?',
            confirmReactivateTitle: '¿Reactivar Usuario?',
            confirmReactivateText: '¿Seguro que deseas reactivar este usuario?',
            btnCancel: 'Cancelar',
            btnConfirmDisable: 'Deshabilitar',
            btnConfirmReactivate: 'Reactivar'
        },
        en: {
            pageTitle: '👥 User List',
            createBtn: '+ Create User',
            thNombre: 'Name',
            thTipoIdentificacion: 'ID Type',
            thNumeroIdentificacion: 'ID Number',
            thTipo: 'Type',
            thEstado: 'Status',
            thAcciones: 'Actions',
            emptyStateText: 'No users registered in the system.',
            actionEdit: 'Edit',
            actionDisable: 'Disable',
            actionReactivate: 'Reactivate',
            footerMainText: 'Central System List - SENA',
            footerSubtext: 'Sustainable digital art',
            footerCopyright: '© 2024 User Control System. All rights reserved.',
            message: 'Settings saved!',
            confirmDisableTitle: 'Disable User?',
            confirmDisableText: 'Are you sure you want to disable this user?',
            confirmReactivateTitle: 'Reactivate User?',
            confirmReactivateText: 'Are you sure you want to reactivate this user?',
            btnCancel: 'Cancel',
            btnConfirmDisable: 'Disable',
            btnConfirmReactivate: 'Reactivate'
        }
    };

    function togglePanel() {
        configPanel.classList.toggle('show');
        configOverlay.classList.toggle('show');
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    function applyLanguage(lang) {
        const t = translations[lang] || translations.es;
        Object.keys(t).forEach(key => {
            const el = document.getElementById(key);
            if (el) el.textContent = t[key];
        });
        
        // Actualizar textos de acciones
        document.querySelectorAll('.action-text').forEach(span => {
            const parent = span.closest('a, button');
            if (parent.classList.contains('edit')) {
                span.textContent = t.actionEdit;
            } else if (parent.classList.contains('btn-disable')) {
                span.textContent = t.actionDisable;
            } else if (parent.classList.contains('btn-reactivate')) {
                span.textContent = t.actionReactivate;
            }
        });
        
        // Actualizar textos del footer
        const footerMainText = document.querySelector('.footer-main-text');
        const footerSubtext = document.querySelector('.footer-subtext');
        const footerCopyright = document.querySelector('.footer-copyright p');
        
        if (footerMainText) footerMainText.textContent = t.footerMainText;
        if (footerSubtext) footerSubtext.textContent = t.footerSubtext;
        if (footerCopyright) footerCopyright.textContent = t.footerCopyright;
        
        configMessage.textContent = t.message;
    }

    function loadSettings() {
        const saved = JSON.parse(localStorage.getItem('userSettings') || '{}');
        themeSelect.value = saved.theme || 'light';
        notificationsSelect.value = saved.notifications || 'enabled';
        languageSelect.value = saved.language || 'es';
        resultsInput.value = saved.resultsPerPage || 10;
        applyTheme(themeSelect.value);
        applyLanguage(languageSelect.value);
    }

    function saveSettings() {
        const settings = {
            theme: themeSelect.value,
            notifications: notificationsSelect.value,
            language: languageSelect.value,
            resultsPerPage: resultsInput.value
        };
        localStorage.setItem('userSettings', JSON.stringify(settings));
        applyTheme(settings.theme);
        applyLanguage(settings.language);
        configMessage.style.display = 'block';
        setTimeout(() => {
            configMessage.style.display = 'none';
            togglePanel();
        }, 1500);
    }

    configLink.addEventListener('click', e => {
        e.preventDefault();
        loadSettings();
        togglePanel();
    });
    
    if (cancelConfigBtn) {
        cancelConfigBtn.addEventListener('click', togglePanel);
    }
    
    if (saveConfigBtn) {
        saveConfigBtn.addEventListener('click', saveSettings);
    }
    
    if (configOverlay) {
        configOverlay.addEventListener('click', togglePanel);
    }

    loadSettings();

    // =========================
    // MODAL DE CONFIRMACIÓN PARA USUARIOS
    // =========================
    const disableForms = document.querySelectorAll('form[action*="deshabilitar_usuario"]');
    const reactivateForms = document.querySelectorAll('form[action*="reactivar_usuario"]');

    // Crear modal dinámicamente
    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3 id="confirmTitle">¿Deshabilitar Usuario?</h3>
            <p id="confirmText">¿Seguro que deseas deshabilitar este usuario?</p>
            <div class="modal-buttons">
                <button id="modalCancel" class="cancel-btn">Cancelar</button>
                <button id="modalConfirm" class="confirm-btn">Deshabilitar</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    const modalCancel = modal.querySelector('#modalCancel');
    const modalConfirm = modal.querySelector('#modalConfirm');
    const confirmTitle = modal.querySelector('#confirmTitle');
    const confirmText = modal.querySelector('#confirmText');

    let formToSubmit = null;
    let currentActionType = ''; // 'disable' o 'reactivate'

    // Configurar forms de deshabilitar
    disableForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            formToSubmit = form;
            currentActionType = 'disable';
            
            const t = translations[languageSelect.value] || translations.es;
            confirmTitle.textContent = t.confirmDisableTitle;
            confirmText.textContent = t.confirmDisableText;
            modalConfirm.textContent = t.btnConfirmDisable;
            modalConfirm.style.background = '#dc3545';
            
            modal.classList.add('show');
        });
    });

    // Configurar forms de reactivar
    reactivateForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            formToSubmit = form;
            currentActionType = 'reactivate';
            
            const t = translations[languageSelect.value] || translations.es;
            confirmTitle.textContent = t.confirmReactivateTitle;
            confirmText.textContent = t.confirmReactivateText;
            modalConfirm.textContent = t.btnConfirmReactivate;
            modalConfirm.style.background = '#28a745';
            
            modal.classList.add('show');
        });
    });

    modalCancel.addEventListener('click', () => {
        modal.classList.remove('show');
        formToSubmit = null;
        currentActionType = '';
    });

    modalConfirm.addEventListener('click', () => {
        if (formToSubmit) {
            formToSubmit.submit();
        }
        modal.classList.remove('show');
        formToSubmit = null;
        currentActionType = '';
    });

    // Actualizar textos del modal cuando cambie el idioma
    languageSelect.addEventListener('change', () => {
        const t = translations[languageSelect.value] || translations.es;
        modalCancel.textContent = t.btnCancel;
        
        if (currentActionType === 'disable') {
            confirmTitle.textContent = t.confirmDisableTitle;
            confirmText.textContent = t.confirmDisableText;
            modalConfirm.textContent = t.btnConfirmDisable;
        } else if (currentActionType === 'reactivate') {
            confirmTitle.textContent = t.confirmReactivateTitle;
            confirmText.textContent = t.confirmReactivateText;
            modalConfirm.textContent = t.btnConfirmReactivate;
        }
    });
});