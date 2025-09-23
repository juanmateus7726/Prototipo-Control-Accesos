document.addEventListener('DOMContentLoaded', function() {
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
                    pageTitle: '🏫 Lista de Ambientes',
                    createBtn: '+ Crear Ambiente',
                    thNombre: 'Nombre',
                    thCodigo: 'Código',
                    thEstado: 'Estado',
                    thCapacidad: 'Capacidad',
                    thAcciones: 'Acciones',
                    emptyStateText: 'No hay ambientes registrados en el sistema.',
                    actionEdit: 'Editar',
                    actionDelete: 'Eliminar',
                    footerText1: 'Sistema de Control de Ambientes - SENA',
                    footerText2: 'Todos los derechos reservados',
                    message: '¡Configuración guardada!'
                },
                en: {
                    pageTitle: '🏫 Room List',
                    createBtn: '+ Create Room',
                    thNombre: 'Name',
                    thCodigo: 'Code',
                    thEstado: 'Status',
                    thCapacidad: 'Capacity',
                    thAcciones: 'Actions',
                    emptyStateText: 'No rooms registered in the system.',
                    actionEdit: 'Edit',
                    actionDelete: 'Delete',
                    footerText1: 'Room Control System - SENA',
                    footerText2: 'All rights reserved',
                    message: 'Settings saved!'
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
                document.querySelectorAll('.action-text').forEach(span => {
                    const parent = span.closest('a');
                    span.textContent = parent.classList.contains('edit') ? t.actionEdit : t.actionDelete;
                });
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
                setTimeout(() => { configMessage.style.display = 'none'; togglePanel(); }, 1500);
            }

            configLink.addEventListener('click', e => { e.preventDefault(); loadSettings(); togglePanel(); });
            closeConfigBtn.addEventListener('click', togglePanel);
            cancelConfigBtn.addEventListener('click', togglePanel);
            configOverlay.addEventListener('click', togglePanel);
            saveConfigBtn.addEventListener('click', saveSettings);
            loadSettings();
        });