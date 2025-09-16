// Base de datos simulada
        const usuarios = {
            "12345678": {
                nombre: "Juan Pérez",
                tipo: "instructor",
                areas_permitidas: ["quimica", "carbones", "biotecnologia", "sistemas"],
                activo: true
            },
            "87654321": {
                nombre: "María García", 
                tipo: "aprendiz",
                areas_permitidas: ["quimica", "sistemas", "bilinguismo"],
                activo: true
            },
            "11111111": {
                nombre: "Carlos Admin",
                tipo: "administrativo", 
                areas_permitidas: ["todos"],
                activo: true
            },
            "22222222": {
                nombre: "Ana Visitante",
                tipo: "visitante",
                areas_permitidas: ["sistemas"],
                activo: true
            },
            "99999999": {
                nombre: "Usuario Restringido",
                tipo: "restringido",
                areas_permitidas: [],
                activo: false
            },
            "55555555": {
                nombre: "Pedro Instructor Minería",
                tipo: "instructor",
                areas_permitidas: ["abc_maquinaria", "minas_didacticas", "beneficios"],
                activo: true
            }
        };

        const ambientes = {
            quimica: {
                nombre: "Laboratorio de Química Aplicada",
                protocolo: "⚠️ OBLIGATORIO: Usar bata, gafas de seguridad y guantes. Prohibido ingresar con comida o bebidas. Verificar ducha de emergencia.",
                riesgo: "alto"
            },
            carbones: {
                nombre: "Laboratorio de Carbones", 
                protocolo: "⚠️ OBLIGATORIO: Usar mascarilla antipolvo N95, ropa de trabajo y calzado cerrado. Verificar sistema de ventilación activo.",
                riesgo: "alto"
            },
            biotecnologia: {
                nombre: "Laboratorio de Biotecnología",
                protocolo: "⚠️ OBLIGATORIO: Esterilizar manos, usar bata estéril y gorro. Prohibido ingreso de material contaminado. Zona estéril.",
                riesgo: "medio"
            },
            beneficios: {
                nombre: "Lab. Beneficios Minerales",
                protocolo: "⚠️ OBLIGATORIO: Casco, gafas de seguridad, calzado de seguridad y guantes. Verificar equipos de trituración antes del uso.",
                riesgo: "alto"
            },
            aguas: {
                nombre: "Laboratorio de Aguas",
                protocolo: "⚠️ OBLIGATORIO: Bata, gafas y guantes de nitrilo. Manipular reactivos químicos con extrema precaución. Lavaojos disponible.",
                riesgo: "medio"
            },
            suelos: {
                nombre: "Laboratorio de Suelos",
                protocolo: "⚠️ OBLIGATORIO: Usar guantes y mascarilla. Manipular muestras con instrumentos adecuados. Evitar inhalación de partículas.",
                riesgo: "bajo"
            },
            abc_maquinaria: {
                nombre: "Ambiente ABC - Maquinaria Pesada",
                protocolo: "🚨 PELIGRO EXTREMO: Casco, botas de seguridad con puntera, chaleco reflectivo, gafas OBLIGATORIOS. Instructor certificado requerido. Prohibido operar sin autorización.",
                riesgo: "muy_alto"
            },
            bilinguismo: {
                nombre: "Ambiente de Bilingüismo",
                protocolo: "ℹ️ Ambiente de estudio. Mantener silencio y orden. Dispositivos en modo silencioso.",
                riesgo: "bajo"
            },
            sistemas: {
                nombre: "Laboratorio de Sistemas",
                protocolo: "💻 Prohibido ingresar líquidos cerca de equipos. Usar credenciales de red asignadas. No modificar configuraciones sin autorización.",
                riesgo: "bajo"
            },
            minas_didacticas: {
                nombre: "Minas Didácticas",
                protocolo: "🚨 RIESGO EXTREMO: Casco minero, botas especializadas, chaleco reflectivo, lámpara minera, detector de gases, arnés de seguridad OBLIGATORIOS. Instructor especializado y protocolo de emergencia activo.",
                riesgo: "muy_alto"
            }
        };

        let ambienteActual = "sistemas";
        let cameraActive = false;
        let stream = null;

        // Inicializar interfaz
        document.addEventListener('DOMContentLoaded', function() {
            cargarUsuariosPrueba();
            actualizarInfoAmbiente();
            agregarLog("🟢 Sistema iniciado correctamente");
        });

        function cargarUsuariosPrueba() {
            const grid = document.getElementById('usersGrid');
            grid.innerHTML = '';
            
            Object.entries(usuarios).forEach(([carnet, user]) => {
                const userCard = document.createElement('div');
                userCard.className = `user-card ${user.tipo}`;
                userCard.onclick = () => probarUsuarioDesdeGrid(carnet);
        
                const estado = user.activo ? '✅' : '❌';
                const areas = user.areas_permitidas.includes('todos') ? 
                    'Todas' : user.areas_permitidas.join(', ');
        
                userCard.innerHTML = `
                    <div style="font-weight: 600; color: #2c3e50;">
                        ${estado} ${user.nombre}
                    </div>
                    <div style="color: #7f8c8d; font-size: 0.9rem;">
                        🎫 ${carnet}
                    </div>
                    <div style="color: #7f8c8d; font-size: 0.9rem;">
                        👤 ${user.tipo}
                    </div>
                    <div style="color: #7f8c8d; font-size: 0.8rem;">
                        📍 ${areas}
                    </div>
                    <div style="margin-top: 8px;">
                        <small style="color: #3498db; cursor: pointer;">
                            👆 Seleccionar para prueba
                        </small>
                    </div>
                `;
        
                grid.appendChild(userCard);
            });
        }

        function probarUsuario(carnet) {
            document.getElementById('carnetInput').value = carnet;
            verificarAcceso(carnet, 'testing');
        }

        function cambiarAmbiente() {
            const select = document.getElementById('ambienteSelect');
            ambienteActual = select.value;
            actualizarInfoAmbiente();
            agregarLog(`📍 Ambiente cambiado a: ${ambientes[ambienteActual].nombre}`);
            mostrarNotificacion(`Ambiente cambiado a ${ambientes[ambienteActual].nombre}`, 'info');
        }

        function actualizarInfoAmbiente() {
            const ambiente = ambientes[ambienteActual];
            const infoElement = document.getElementById('ambienteInfo');
            
            const riskClass = `risk-${ambiente.riesgo}`;
            infoElement.innerHTML = `
                ${ambiente.nombre}
                <span class="risk-indicator ${riskClass}">Riesgo: ${ambiente.riesgo.replace('_', ' ')}</span>
            `;
        }

        async function toggleCamera() {
            if (!cameraActive) {
                await activarCamera();
            } else {
                detenerCamera();
            }
        }

        async function activarCamera() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.getElementById('videoElement');
                const status = document.getElementById('cameraStatus');
                const overlay = document.getElementById('cameraOverlay');
                const detection = document.getElementById('faceDetection');
                
                video.srcObject = stream;
                video.style.display = 'block';
                status.style.display = 'none';
                overlay.style.display = 'block';
                detection.style.display = 'block';
                detection.classList.add('detecting');
                
                cameraActive = true;
                document.getElementById('cameraButtonText').textContent = 'Detener Cámara';
                
                agregarLog("📹 Cámara activada - Sistema de reconocimiento facial operativo");
                mostrarNotificacion("Cámara activada correctamente", 'success');
                
            } catch (error) {
                console.error('Error accessing camera:', error);
                mostrarNotificacion("Error: No se pudo acceder a la cámara", 'error');
                agregarLog("❌ Error al activar cámara: " + error.message);
            }
        }

        function detenerCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            const video = document.getElementById('videoElement');
            const status = document.getElementById('cameraStatus');
            const overlay = document.getElementById('cameraOverlay');
            const detection = document.getElementById('faceDetection');
            
            video.style.display = 'none';
            status.style.display = 'block';
            overlay.style.display = 'none';
            detection.style.display = 'none';
            detection.classList.remove('detecting');
            
            status.innerHTML = '📹 CÁMARA DESACTIVADA<br><small>Presiona "Activar Cámara" para iniciar</small>';
            
            cameraActive = false;
            document.getElementById('cameraButtonText').textContent = 'Activar Cámara';
            
            agregarLog("📹 Cámara desactivada");
        }

        function simularReconocimiento() {
            if (!cameraActive) {
                mostrarNotificacion("Activa la cámara primero", 'error');
                return;
            }
            
            const carnets = Object.keys(usuarios);
            const carnetAleatorio = carnets[Math.floor(Math.random() * carnets.length)];
            
            // Efecto visual de reconocimiento
            const overlay = document.getElementById('cameraOverlay');
            overlay.innerHTML = '<div class="loading"></div> Analizando rostro...';
            
            agregarLog("🔍 Iniciando análisis de reconocimiento facial...");
            
            setTimeout(() => {
                overlay.innerHTML = '✅ Rostro detectado y analizado';
                setTimeout(() => {
                    verificarAcceso(carnetAleatorio, 'reconocimiento_facial');
                    overlay.innerHTML = '🔍 Buscando rostros...';
                }, 1000);
            }, 2000);
        }

        function verificarCarnetManual() {
            const carnet = document.getElementById('carnetInput').value.trim();
            if (!carnet) {
                mostrarNotificacion("Ingrese un número de carnet", 'error');
                return;
            }
            verificarAcceso(carnet, 'carnet_manual');
            document.getElementById('carnetInput').value = '';
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                verificarCarnetManual();
            }
        }

        function verificarAcceso(carnet, metodo) {
            const timestamp = new Date().toLocaleTimeString();
            
            if (!usuarios[carnet]) {
                denegarAcceso("Usuario no registrado en el sistema", carnet, metodo);
                return;
            }
            
            const usuario = usuarios[carnet];
            
            if (!usuario.activo) {
                denegarAcceso("Usuario inactivo o con acceso restringido", carnet, metodo);
                return;
            }
            
            if (!tienePermiso(usuario, ambienteActual)) {
                denegarAcceso(`Sin autorización para ${ambientes[ambienteActual].nombre}`, carnet, metodo);
                return;
            }
            
            permitirAcceso(usuario, carnet, metodo);
        }

        function tienePermiso(usuario, ambiente) {
            return usuario.areas_permitidas.includes("todos") || 
                    usuario.areas_permitidas.includes(ambiente);
        }

        function permitirAcceso(usuario, carnet, metodo) {
            const timestamp = new Date().toLocaleTimeString();
            const ambiente = ambientes[ambienteActual];
            
            // Actualizar estado visual
            const statusEl = document.getElementById('statusIndicator');
            statusEl.className = 'status-indicator status-granted';
            statusEl.innerHTML = '🟢 ACCESO PERMITIDO<br><small>¡Bienvenido al centro!</small>';
            
            // Información del usuario
            const userInfoEl = document.getElementById('userInfo');
            userInfoEl.innerHTML = `
                <div style="text-align: left; background: rgba(46, 204, 113, 0.1); padding: 15px; border-radius: 10px;">
                    <strong>👤 Usuario:</strong> ${usuario.nombre}<br>
                    <strong>🎫 Carnet:</strong> ${carnet}<br>
                    <strong>👨‍💼 Tipo:</strong> ${usuario.tipo.toUpperCase()}<br>
                    <strong>🏢 Ambiente:</strong> ${ambiente.nombre}<br>
                    <strong>⏰ Hora de ingreso:</strong> ${timestamp}<br>
                    <strong>🔍 Método:</strong> ${metodo.replace('_', ' ').toUpperCase()}
                </div>
            `;
            
            // Log detallado
            const logEntry = `✅ ${timestamp} - ACCESO PERMITIDO
    ${usuario.nombre} (${carnet}) - ${usuario.tipo}
    Ambiente: ${ambiente.nombre}
    Método: ${metodo.replace('_', ' ')}`;
            
            agregarLog(logEntry);
            
            // Mostrar protocolo
            mostrarProtocolo(ambiente);
            
            // Notificación
            mostrarNotificacion(`Acceso permitido para ${usuario.nombre}`, 'success');
            
            // Auto-reset después de 8 segundos
            setTimeout(resetearEstado, 8000);
        }

        function denegarAcceso(razon, carnet, metodo) {
            const timestamp = new Date().toLocaleTimeString();
            
            // Actualizar estado visual
            const statusEl = document.getElementById('statusIndicator');
            statusEl.className = 'status-indicator status-denied';
            statusEl.innerHTML = `🔴 ACCESO DENEGADO<br><small>${razon}</small>`;
            
            // Información del intento
            const userInfoEl = document.getElementById('userInfo');
            userInfoEl.innerHTML = `
                <div style="text-align: left; background: rgba(231, 76, 60, 0.1); padding: 15px; border-radius: 10px;">
                    <strong>❌ Acceso Denegado</strong><br>
                    <strong>🎫 Carnet:</strong> ${carnet}<br>
                    <strong>📍 Ambiente:</strong> ${ambientes[ambienteActual].nombre}<br>
                    <strong>⚠️ Razón:</strong> ${razon}<br>
                    <strong>⏰ Hora:</strong> ${timestamp}<br>
                    <strong>🔍 Método:</strong> ${metodo.replace('_', ' ').toUpperCase()}
                </div>
            `;
            
            // Log
            const logEntry = `❌ ${timestamp} - ACCESO DENEGADO
    Carnet: ${carnet}
    Razón: ${razon}
    Ambiente: ${ambientes[ambienteActual].nombre}
    Método: ${metodo.replace('_', ' ')}`;
            
            agregarLog(logEntry);
            
            // Notificación
            mostrarNotificacion(`Acceso denegado: ${razon}`, 'error');
            
            // Auto-reset después de 5 segundos
            setTimeout(resetearEstado, 5000);
        }

        function mostrarProtocolo(ambiente) {
            const modal = document.getElementById('protocolModal');
            const title = document.getElementById('protocolTitle');
            const text = document.getElementById('protocolText');
            
            title.textContent = `Protocolo de Seguridad - ${ambiente.nombre}`;
            text.textContent = ambiente.protocolo;
            
            modal.style.display = 'flex';
            
            // Log del protocolo mostrado
            agregarLog(`📋 Protocolo de seguridad mostrado para ${ambiente.nombre}`);
        }

        function cerrarProtocolo() {
            document.getElementById('protocolModal').style.display = 'none';
        }

        function resetearEstado() {
            const statusEl = document.getElementById('statusIndicator');
            statusEl.className = 'status-indicator status-denied';
            statusEl.innerHTML = '🔴 ACCESO DENEGADO<br><small>Esperando identificación...</small>';
            
            document.getElementById('userInfo').innerHTML = 
                '<p style="color: #7f8c8d; font-style: italic;">No hay usuario identificado</p>';
        }

        function agregarLog(mensaje) {
            const logContainer = document.getElementById('logContainer');
            const timestamp = new Date().toLocaleString();
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `<span style="color: #74b9ff;">[${timestamp}]</span> ${mensaje}`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        function mostrarNotificacion(mensaje, tipo) {
            const notification = document.getElementById('notification');
            notification.textContent = mensaje;
            notification.className = `notification ${tipo}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 4000);
        }

        // Cerrar modal con ESC
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                cerrarProtocolo();
            }
        });

        // Cerrar modal al hacer clic fuera
        document.getElementById('protocolModal').addEventListener('click', function(event) {
            if (event.target === this) {
                cerrarProtocolo();
            }
        });



        // Mejorar la experiencia de usuario
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar el formulario cuando cambie el ambiente seleccionado
    document.getElementById('ambienteSelect').addEventListener('change', function() {
        const laboratorioSelect = document.getElementById('laboratorio-select');
        laboratorioSelect.value = this.value;
    });
    
    // Validación del formulario
    document.getElementById('accesoForm').addEventListener('submit', function(e) {
        const usuario = document.getElementById('usuario-select').value;
        const laboratorio = document.getElementById('laboratorio-select').value;
        const metodo = document.getElementById('metodo-select').value;
        
        if (!usuario || !laboratorio || !metodo) {
            e.preventDefault();
            mostrarNotificacion('Por favor complete todos los campos', 'error');
        }
    });
    
    // Cargar usuarios en el grid de prueba
    cargarUsuariosPrueba();
});

// Función para probar usuario desde el grid
function probarUsuarioDesdeGrid(usuarioId) {
    const select = document.getElementById('usuario-select');
    select.value = usuarioId;
    
    // Simular verificación de acceso
    const usuario = select.options[select.selectedIndex];
    const carnet = usuario.textContent.match(/\((\d+)\)/)[1];
    verificarAcceso(carnet, 'seleccion_manual');
}