document.addEventListener('DOMContentLoaded', function() {
            // === Script del panel de configuración (igual al de editar_usuario) ===
            const configLink = document.getElementById('configLink');
            const configPanel = document.getElementById('configPanel');
            const closeConfigBtn = document.getElementById('closeConfig');
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
                    footerText1: 'Access Control System - SENA',
                    footerText2: 'All rights reserved',
                    linkPrivacy: 'Privacy Policy',
                    linkTerms: 'Terms of Use',
                    linkSupport: 'Technical Support',
                    message: 'Settings saved!'
                }
            };

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
                document.querySelectorAll('[id]').forEach(el => {
                    if (currentLang[el.id]) el.textContent = currentLang[el.id];
                });
                configMessage.textContent = currentLang.message;
            }

            function loadSettings() {
                const saved = localStorage.getItem('userSettings');
                if (saved) {
                    const s = JSON.parse(saved);
                    themeSelect.value = s.theme || 'light';
                    notificationsSelect.value = s.notifications || 'enabled';
                    languageSelect.value = s.language || 'es';
                    resultsInput.value = s.resultsPerPage || 10;
                    applyTheme(s.theme);
                    applyLanguage(s.language);
                }
            }

            function saveSettings() {
                const s = {
                    theme: themeSelect.value,
                    notifications: notificationsSelect.value,
                    language: languageSelect.value,
                    resultsPerPage: resultsInput.value
                };
                localStorage.setItem('userSettings', JSON.stringify(s));
                applyTheme(s.theme);
                applyLanguage(s.language);
                configMessage.style.display = 'block';
                setTimeout(() => { configMessage.style.display='none'; toggleConfigPanel(); },1500);
            }

            configLink.addEventListener('click', e => { e.preventDefault(); loadSettings(); toggleConfigPanel(); });
            closeConfigBtn.addEventListener('click', () => { loadSettings(); toggleConfigPanel(); });
            cancelConfigBtn.addEventListener('click', () => { loadSettings(); toggleConfigPanel(); });
            saveConfigBtn.addEventListener('click', saveSettings);
            configOverlay.addEventListener('click', () => { loadSettings(); toggleConfigPanel(); });

            loadSettings();

            // === Confirmación de eliminación ===
            document.getElementById('formEliminar').addEventListener('submit', function(e) {
                if (!confirm('¿Seguro que deseas eliminar este usuario?')) {
                    e.preventDefault();
                }
            });
        });