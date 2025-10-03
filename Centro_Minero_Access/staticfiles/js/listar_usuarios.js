document.addEventListener('DOMContentLoaded', function () {
    // ==============================
    // Variables principales
    // ==============================
    const configLink = document.getElementById('configLink');
    const configPanel = document.getElementById('configPanel');
    const closeConfigBtn = document.getElementById('closeConfig');
    const cancelConfigBtn = document.getElementById('cancelConfig');
    const saveConfigBtn = document.getElementById('saveConfig');
    const configOverlay = document.getElementById('configOverlay');
    const configMessage = document.getElementById('configMessage');

    // Configuración
    const themeSelect = document.getElementById('theme');
    const notificationsSelect = document.getElementById('notifications');
    const languageSelect = document.getElementById('language');
    const resultsInput = document.getElementById('resultsPerPage');

    // ==============================
    // Traducciones
    // ==============================
    const translations = {
        es: {
            brandTitle: 'Control de Accesos',
            brandSubtitle: 'SENA - Centro de Formación',
            navInicio: 'Inicio',
            navUsuarios: 'Usuarios',
            navRegistros: 'Registros',
            navConfiguracion: 'Configuración',
            panelTitle: 'Configuración del Sistema',
            labelTheme: 'Tema de la interfaz',
            optLight: 'Claro',
            optDark: 'Oscuro',
            optAuto: 'Automático',
            labelNotifications: 'Notificaciones',
            optEnabled: 'Activadas',
            optDisabled: 'Desactivadas',
            labelLanguage: 'Idioma',
            labelResults: 'Resultados por página',
            btnCancel: 'Cancelar',
            btnSave: 'Guardar',
            pageTitle: '👥 Lista de Usuarios',
            createBtn: '+ Crear Usuario',
            thNombre: 'Nombre',
            thCarnet: 'Carnet',
            thTipo: 'Tipo',
            thAcciones: 'Acciones',
            emptyStateText: 'No hay usuarios registrados en el sistema.',
            actionEdit: 'Editar',
            actionDelete: 'Eliminar',
            footerText1: 'Sistema de Control de Accesos - SENA',
            footerText2: 'Todos los derechos reservados',
            linkPrivacy: 'Políticas de Privacidad',
            linkTerms: 'Términos de Uso',
            linkSupport: 'Soporte Técnico',
            message: '¡Configuración guardada!'
        },
        en: {
            brandTitle: 'Access Control',
            brandSubtitle: 'SENA - Training Center',
            navInicio: 'Home',
            navUsuarios: 'Users',
            navRegistros: 'Logs',
            navConfiguracion: 'Settings',
            panelTitle: 'System Settings',
            labelTheme: 'Interface Theme',
            optLight: 'Light',
            optDark: 'Dark',
            optAuto: 'Auto',
            labelNotifications: 'Notifications',
            optEnabled: 'Enabled',
            optDisabled: 'Disabled',
            labelLanguage: 'Language',
            labelResults: 'Results per page',
            btnCancel: 'Cancel',
            btnSave: 'Save',
            pageTitle: '👥 User List',
            createBtn: '+ Create User',
            thNombre: 'Name',
            thCarnet: 'ID Number',
            thTipo: 'Type',
            thAcciones: 'Actions',
            emptyStateText: 'No users are registered in the system.',
            actionEdit: 'Edit',
            actionDelete: 'Delete',
            footerText1: 'Access Control System - SENA',
            footerText2: 'All rights reserved',
            linkPrivacy: 'Privacy Policy',
            linkTerms: 'Terms of Use',
            linkSupport: 'Technical Support',
            message: 'Settings saved!'
        }
    };

    // ==============================
    // Funciones de configuración
    // ==============================
    function toggleConfigPanel() {
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
        const currentLang = translations[lang] || translations.es;
        document.querySelectorAll('[id]').forEach(element => {
            const translationKey = element.id;
            if (currentLang[translationKey]) {
                if (element.tagName === 'A' && element.classList.contains('create-btn')) {
                    element.textContent = currentLang[translationKey];
                } else {
                    element.textContent = currentLang[translationKey];
                }
            }
        });

        // Botones de acción en la tabla
        document.querySelectorAll('.action-text').forEach(actionSpan => {
            const parentLink = actionSpan.closest('a');
            if (parentLink.classList.contains('edit')) {
                actionSpan.textContent = currentLang.actionEdit;
            } else if (parentLink.classList.contains('delete')) {
                actionSpan.textContent = currentLang.actionDelete;
            }
        });

        configMessage.textContent = currentLang.message;
    }

    function loadSettings() {
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            themeSelect.value = settings.theme || 'light';
            notificationsSelect.value = settings.notifications || 'enabled';
            languageSelect.value = settings.language || 'es';
            resultsInput.value = settings.resultsPerPage || 10;
            applySettings(settings);
        }
    }

    function applySettings(settings) {
        applyTheme(settings.theme);
        applyLanguage(settings.language);
    }

    function saveSettings() {
        const settings = {
            theme: themeSelect.value,
            notifications: notificationsSelect.value,
            language: languageSelect.value,
            resultsPerPage: resultsInput.value
        };
        localStorage.setItem('userSettings', JSON.stringify(settings));

        applySettings(settings);

        configMessage.style.display = 'block';
        setTimeout(() => {
            configMessage.style.display = 'none';
            toggleConfigPanel();
        }, 1500);
    }

    // ==============================
    // Event Listeners
    // ==============================
    configLink.addEventListener('click', function (event) {
        event.preventDefault();
        loadSettings();
        toggleConfigPanel();
    });

    closeConfigBtn.addEventListener('click', function () {
        loadSettings();
        toggleConfigPanel();
    });

    cancelConfigBtn.addEventListener('click', function () {
        loadSettings();
        toggleConfigPanel();
    });

    saveConfigBtn.addEventListener('click', saveSettings);

    configOverlay.addEventListener('click', function () {
        loadSettings();
        toggleConfigPanel();
    });

    // Cargar la configuración al iniciar
    loadSettings();

    // ==============================
    // Preparar sistema de Deshabilitar / Reactivar usuarios
    // ==============================
    // Aquí añadiremos las funciones y listeners cuando implementemos el sistema:
    // - Botón de deshabilitar
    // - Botón de reactivar
    // - Confirmaciones
    // - Cambio de estado dinámico
});
