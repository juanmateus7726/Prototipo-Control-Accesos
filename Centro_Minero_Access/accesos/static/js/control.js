/* =========================
   VARIABLES GLOBALES
   ========================= */
let ambienteActual = "sistemas";
let cameraActive = false;
let stream = null;

/* =========================
   FUNCIONES DE INTERFAZ
   ========================= */
// Nota: La función cargarUsuariosPrueba ya no es necesaria si usas datos de la base de datos de Django

function probarUsuarioDesdeGrid(carnet) {
    const select = document.getElementById("id_usuario");
    if (select) {
        select.value = carnet;
        select.dispatchEvent(new Event("change"));
    }
    // Nota: La función verificarAcceso debe ser implementada para interactuar con el backend de Django
    // En el código actual, la lógica de verificación de acceso se maneja en el backend al enviar el formulario
}

/* =========================
   AMBIENTE Y PROTOCOLO
   ========================= */
function cambiarAmbiente() {
    const select = document.getElementById("ambienteSelect");
    const infoDiv = document.getElementById("ambienteInfo");
    
    // Obtiene el nombre del ambiente seleccionado
    const selectedOption = select.options[select.selectedIndex];
    const ambienteNombre = selectedOption.textContent;

    // Aquí es donde el código se vuelve dinámico
    // Construimos la URL para la vista de Django
    const url = "{% url 'accesos:obtener_riesgo' %}?ambiente_nombre=" + encodeURIComponent(ambienteNombre);

    // Hacemos una petición a Django para obtener el riesgo
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ambiente no encontrado');
            }
            return response.json();
        })
        .then(data => {
            const riesgo = data.riesgo;
            const descripcionRiesgo = data.descripcion_riesgo;

            // Asignamos la clase CSS según el nivel de riesgo
            let claseRiesgo = '';
            if (riesgo === 'bajo') {
                claseRiesgo = 'risk-bajo';
            } else if (riesgo === 'medio') {
                claseRiesgo = 'risk-medio';
            } else if (riesgo === 'alto') {
                claseRiesgo = 'risk-alto';
            } else if (riesgo === 'muy_alto') {
                claseRiesgo = 'risk-muy-alto';
            } else {
                claseRiesgo = 'risk-desconocido';
            }
            
            // Actualizamos el HTML para mostrar el riesgo y el nombre
            infoDiv.innerHTML = `${ambienteNombre} <span class="risk-indicator ${claseRiesgo}">Riesgo: ${descripcionRiesgo}</span>`;
            agregarLog(`📍 Ambiente cambiado a: ${ambienteNombre}`);
        })
        .catch(error => {
            console.error('Error al obtener el riesgo:', error);
            infoDiv.innerHTML = `${ambienteNombre} <span class="risk-indicator risk-desconocido">Riesgo: Desconocido</span>`;
            agregarLog(`❌ Error al cargar el ambiente: ${ambienteNombre}`);
        });
}


/* =========================
   CÁMARA Y RECONOCIMIENTO
   ========================= */
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
        const video = document.getElementById("videoElement");
        const status = document.getElementById("cameraStatus");
        const overlay = document.getElementById("cameraOverlay");
        const detection = document.getElementById("faceDetection");

        if (video) video.srcObject = stream;
        if (video) video.style.display = "block";
        if (status) status.style.display = "none";
        if (overlay) overlay.style.display = "block";
        if (detection) detection.style.display = "block";

        cameraActive = true;
        document.getElementById("cameraButtonText").textContent = "Detener Cámara";
        agregarLog("📹 Cámara activada");
    } catch (error) {
        agregarLog("❌ Error al activar cámara: " + error.message);
    }
}

function detenerCamera() {
    if (stream) stream.getTracks().forEach((t) => t.stop());
    const video = document.getElementById("videoElement");
    const status = document.getElementById("cameraStatus");
    const overlay = document.getElementById("cameraOverlay");
    const detection = document.getElementById("faceDetection");

    if (video) video.style.display = "none";
    if (status) status.style.display = "block";
    if (overlay) overlay.style.display = "none";
    if (detection) detection.style.display = "none";

    cameraActive = false;
    document.getElementById("cameraButtonText").textContent = "Activar Cámara";
}


/* =========================
   ACCESOS
   ========================= */
// Nota: La lógica de `verificarAcceso`, `permitirAcceso` y `denegarAcceso`
// se maneja ahora completamente en el backend de Django, en la vista
// `control_acceso_view`. No es necesario replicarla en el frontend.

function resetearEstado() {
    const status = document.getElementById("statusIndicator");
    const info = document.getElementById("userInfo");
    if (status) {
        status.className = "status-indicator status-denied";
        status.innerHTML = "🔴 ACCESO DENEGADO<br><small>Esperando identificación...</small>";
    }
    if (info) info.innerHTML = "<p style='color:#7f8c8d'>No hay usuario identificado</p>";
}

/* =========================
   LOG Y NOTIFICACIONES
   ========================= */
function agregarLog(msg) {
    const cont = document.getElementById("logContainer");
    if (!cont) return;
    const ts = new Date().toLocaleString();
    const div = document.createElement("div");
    div.innerHTML = `<span style="color:#74b9ff">[${ts}]</span> ${msg}`;
    cont.appendChild(div);
    cont.scrollTop = cont.scrollHeight;
}

/* =========================
   INICIALIZACIÓN
   ========================= */
document.addEventListener("DOMContentLoaded", () => {
    // Escuchamos el evento `change` del selector de ambientes
    const ambienteSelect = document.getElementById("ambienteSelect");
    if (ambienteSelect) {
        ambienteSelect.addEventListener("change", cambiarAmbiente);
        // Llamamos a la función al cargar la página para mostrar la información inicial
        cambiarAmbiente();
    }
    // Nota: La lógica de validación de formulario ya se maneja en el backend
});

// Manejo del modal de acceso manual
const modalAccesoManual = document.getElementById('modalAccesoManual');
const btnManual = document.getElementById('btn-acceso-manual');
const customClose = document.querySelector('.custom-close');

btnManual.addEventListener('click', (e) => {
    e.preventDefault();
    detenerReconocimiento(); // Detener cámara si está activa
    const ambienteSelect = document.getElementById('ambienteSelect');
    document.getElementById('modalAmbienteManualHiddenInput').value = ambienteSelect.value;
    modalAccesoManual.style.display = 'block';
});

customClose.addEventListener('click', () => {
    modalAccesoManual.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modalAccesoManual) {
        modalAccesoManual.style.display = 'none';
    }
});

// Manejo del formulario dentro del modal
document.getElementById('modalManualForm').addEventListener('submit', (e) => {
    const input = document.getElementById('modalNumeroIdInput');
    const btn = e.target.querySelector('button[type="submit"]');
    if (!input.value.trim()) {
        e.preventDefault();
        alert('⚠️ Ingrese su número de identificación.');
        return;
    }
    btn.innerHTML = '⏳ Verificando...';
    btn.disabled = true;
});


    document.addEventListener("DOMContentLoaded", () => {
        // Call your exported functions here to test
        SiennaAccessibility.load();
    });


    // Tu código JavaScript existente...
    document.addEventListener('DOMContentLoaded', () => {
        // === NUEVA LÓGICA DE INTERFAZ ===
        const seccionFacial = document.getElementById('seccion-facial');
        const seccionManual = document.getElementById('seccion-manual');
        const btnFacial = document.getElementById('btn-acceso-facial');
        const btnManual = document.getElementById('btn-acceso-manual');

        // Estado inicial
        seccionFacial.style.display = 'block';
        seccionManual.style.display = 'none';

        btnFacial.addEventListener('click', () => {
            seccionFacial.style.display = 'block';
            seccionManual.style.display = 'none';
            btnFacial.classList.add('btn-info', 'active');
            btnFacial.classList.remove('btn-secondary');
            btnManual.classList.remove('btn-info', 'active');
            btnManual.classList.add('btn-secondary');
        });

        btnManual.addEventListener('click', () => {
            detenerReconocimiento(); // Detener la cámara al cambiar de método
            seccionFacial.style.display = 'none';
            seccionManual.style.display = 'block';
            btnManual.classList.add('btn-info', 'active');
            btnManual.classList.remove('btn-secondary');
            btnFacial.classList.remove('btn-info', 'active');
            btnFacial.classList.add('btn-secondary');
        });

        // === LÓGICA EXISTENTE ===
        const manualForm = document.getElementById('manualForm');
        const ambienteSelect = document.getElementById('ambienteSelect');
        const ambienteManualInput = document.getElementById('ambienteManualHiddenInput');

        if (manualForm) {
            manualForm.addEventListener('submit', (e) => {
                // Actualizar el valor del campo oculto antes de enviar
                ambienteManualInput.value = ambienteSelect.value; // <-- Aquí se toma el ID

                const input = document.getElementById('numeroIdInput');
                const btn = manualForm.querySelector('button[type="submit"]');
                if (!input.value.trim()) {
                    e.preventDefault();
                    alert('⚠️ Ingrese su número de identificación.');
                    return;
                }
                btn.innerHTML = '⏳ Verificando...';
                btn.disabled = true;
            });
            
            const input = document.getElementById('numeroIdInput');
            if(input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') manualForm.submit();
                });
            }
        }
        
        cambiarAmbiente(); // Llamar al cargar la página para mostrar el riesgo inicial
    });

    // Variables globales para reconocimiento facial
    let videoStream = null;
    let isRecognitionActive = false;
    let canvas = null;

    // Función para activar reconocimiento facial
    async function activarReconocimiento() {
        try {
            mostrarNotificacion('Iniciando sistema de reconocimiento facial...', 'warning');
            
            const video = document.getElementById('videoElement');
            const cameraStatus = document.getElementById('cameraStatus');
            const cameraOverlay = document.getElementById('cameraOverlay');
            const faceGuide = document.getElementById('faceGuide');
            const reconocimientoBtn = document.getElementById('reconocimientoButtonText');
            const captureBtn = document.getElementById('captureBtn');
            const stopBtn = document.getElementById('stopBtn');

            // Solicitar acceso a la cámara
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });

            video.srcObject = videoStream;
            
            video.onloadedmetadata = () => {
                cameraStatus.style.display = 'none';
                video.style.display = 'block';
                cameraOverlay.style.display = 'flex';
                cameraOverlay.textContent = '🎭 Sistema de reconocimiento activo - Posicione su rostro';
                faceGuide.style.display = 'block';
                
                // Cambiar botones
                document.querySelector('.btn.btn-success').style.display = 'none';
                captureBtn.style.display = 'inline-block';
                stopBtn.style.display = 'inline-block';
                
                isRecognitionActive = true;
                
                mostrarNotificacion('Sistema de reconocimiento facial activado correctamente', 'success');
                agregarLog('Sistema de reconocimiento facial activado');
            };

        } catch (error) {
            console.error('Error al activar reconocimiento:', error);
            mostrarNotificacion('Error al acceder a la cámara. Verifique los permisos.', 'error');
            agregarLog('ERROR: No se pudo acceder a la cámara');
        }
    }

    // Función para capturar y reconocer rostro
    async function capturarRostro() {
        if (!isRecognitionActive) {
            mostrarNotificacion('Active primero el sistema de reconocimiento', 'warning');
            return;
        }

        try {
            mostrarNotificacion('Capturando y analizando rostro...', 'warning');
            agregarLog('Iniciando proceso de reconocimiento...');

            const video = document.getElementById('videoElement');
            
            // Crear canvas para capturar imagen
            if (!canvas) {
                canvas = document.createElement('canvas');
            }
            
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Capturar frame actual
            ctx.drawImage(video, 0, 0);
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Obtener ambiente seleccionado
            const ambienteSelect = document.getElementById('ambienteSelect');
            const ambienteSeleccionado = ambienteSelect.options[ambienteSelect.selectedIndex].text;

            // Enviar para reconocimiento
            const response = await fetch('{% url "usuarios:reconocer_rostro" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({
                    image_data: imageData,
                    ambiente: ambienteSeleccionado
                })
            });

            const data = await response.json();
            
            // Mostrar resultado
            mostrarResultadoReconocimiento(data);
            
            if (data.success && data.acceso_autorizado) {
                actualizarEstadoSistema('approved', data.usuario.nombre);
                mostrarNotificacion(data.message, 'success');
                agregarLog(`ACCESO AUTORIZADO: ${data.usuario.nombre} (${data.confianza}% confianza)`);
                
                // Actualizar tabla de accesos recientes
                actualizarTablaAccesos(data.usuario, ambienteSeleccionado, 'Reconocimiento Facial', data.confianza);
            } else {
                actualizarEstadoSistema('denied');
                mostrarNotificacion(data.message, 'error');
                agregarLog('ACCESO DENEGADO: Rostro no reconocido');
            }

        } catch (error) {
            console.error('Error en reconocimiento:', error);
            mostrarNotificacion('Error al procesar el reconocimiento facial', 'error');
            agregarLog('ERROR: Fallo en el sistema de reconocimiento');
        }
    }

    // Función para detener reconocimiento
    function detenerReconocimiento() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
        }

        const video = document.getElementById('videoElement');
        const cameraStatus = document.getElementById('cameraStatus');
        const cameraOverlay = document.getElementById('cameraOverlay');
        const faceGuide = document.getElementById('faceGuide');
        const captureBtn = document.getElementById('captureBtn');
        const stopBtn = document.getElementById('stopBtn');

        video.style.display = 'none';
        video.srcObject = null;
        cameraStatus.style.display = 'block';
        cameraOverlay.style.display = 'none';
        faceGuide.style.display = 'none';
        
        // Restaurar botones
        document.querySelector('.btn.btn-success').style.display = 'inline-block';
        captureBtn.style.display = 'none';
        stopBtn.style.display = 'none';
        
        isRecognitionActive = false;
        
        // Ocultar resultado
        document.getElementById('reconocimientoResultado').style.display = 'none';
        
        mostrarNotificacion('Sistema de reconocimiento desactivado', 'warning');
        agregarLog('Sistema de reconocimiento desactivado');
        actualizarEstadoSistema('waiting');
    }

    // Función para mostrar resultado del reconocimiento
    function mostrarResultadoReconocimiento(data) {
        const resultado = document.getElementById('reconocimientoResultado');
        const avatar = document.getElementById('avatarUsuario');
        const nombre = document.getElementById('nombreUsuario');
        const carnet = document.getElementById('carnetUsuario');
        const tipo = document.getElementById('tipoUsuario');
        const confianza = document.getElementById('confianzaReconocimiento');
        const status = document.getElementById('accesoStatus');
        
        resultado.style.display = 'block';

        if (data.success && data.acceso_autorizado && data.usuario) {
            // Usuario reconocido
            avatar.textContent = '✅';
            avatar.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
            nombre.textContent = data.usuario.nombre;
            carnet.textContent = `Carnet: ${data.usuario.carnet}`;
            tipo.textContent = `Tipo: ${data.usuario.tipo}`;
            confianza.textContent = `Confianza: ${data.confianza}%`;
            status.innerHTML = '<span class="status-badge status-approved">✅ AUTORIZADO</span>';
        } else {
            // Usuario no reconocido
            avatar.textContent = '❌';
            avatar.style.background = 'linear-gradient(135deg, #dc3545, #c82333)';
            nombre.textContent = 'Usuario Desconocido';
            carnet.textContent = 'Carnet: ----';
            tipo.textContent = 'Tipo: ----';
            confianza.textContent = 'Confianza: --%';
            status.innerHTML = '<span class="status-badge status-denied">❌ DENEGADO</span>';
        }
    }

    // Funciones adicionales (log, notificaciones, etc.)
    function agregarLog(mensaje) {
        const logContainer = document.getElementById('logContainer');
        const nuevoLog = document.createElement('div');
        nuevoLog.textContent = `[${new Date().toLocaleTimeString()}] ${mensaje}`;
        logContainer.prepend(nuevoLog);
        if (logContainer.children.length > 20) {
            logContainer.lastChild.remove();
        }
    }

    function mostrarNotificacion(mensaje, tipo) {
        const notification = document.getElementById('notification');
        notification.textContent = mensaje;
        notification.className = `notification notification-${tipo}`;
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    function actualizarEstadoSistema(status, nombre = 'No hay usuario identificado') {
        const statusIndicator = document.getElementById('statusIndicator');
        const userInfo = document.getElementById('userInfo');
        
        statusIndicator.classList.remove('status-denied', 'status-approved', 'status-waiting');
        userInfo.innerHTML = `<p style="color:#7f8c8d; font-style:italic;">${nombre}</p>`;

        if (status === 'approved') {
            statusIndicator.classList.add('status-approved');
            statusIndicator.innerHTML = '✅ ACCESO AUTORIZADO<br><small>Bienvenido</small>';
        } else if (status === 'denied') {
            statusIndicator.classList.add('status-denied');
            statusIndicator.innerHTML = '🔴 ACCESO DENEGADO<br><small>Esperando identificación...</small>';
        } else {
            statusIndicator.classList.add('status-denied');
            statusIndicator.innerHTML = '🔴 ACCESO DENEGADO<br><small>Esperando identificación...</small>';
        }
    }

    function actualizarTablaAccesos(usuario, ambiente, metodo, confianza) {
        const tbody = document.getElementById('accesosRecentesBody');
        const newRow = tbody.insertRow(0);
        newRow.innerHTML = `
            <td>${usuario.nombre}</td>
            <td>${ambiente}</td>
            <td>${metodo}</td>
            <td>${new Date().toLocaleString()}</td>
            <td>${confianza ? confianza.toFixed(1) + '%' : '--'}</td>
        `;

        if (tbody.rows.length > 10) {
            tbody.deleteRow(10);
        }
    }
    
    // Función para mostrar la información del ambiente
    function cambiarAmbiente() {
    const select = document.getElementById('ambienteSelect');
    const infoDiv = document.getElementById('ambienteInfo');

    const opcionSeleccionada = select.options[select.selectedIndex];

    if (opcionSeleccionada.value === "") {
        infoDiv.innerHTML = "<p class='text-secondary'>Seleccione un ambiente para ver la información.</p>";
        return;
    }

    // Obtener atributos del ambiente
    const codigo = opcionSeleccionada.getAttribute("data-codigo");
    const estado = opcionSeleccionada.getAttribute("data-estado");
    const capacidad = opcionSeleccionada.getAttribute("data-capacidad");
    const riesgo = opcionSeleccionada.getAttribute("data-riesgo");

    // Determinar color de riesgo
    let riesgoClass = "text-secondary";
    if (riesgo.toLowerCase() === "bajo") riesgoClass = "text-success fw-bold";
    if (riesgo.toLowerCase() === "medio") riesgoClass = "text-warning fw-bold";
    if (riesgo.toLowerCase() === "alto") riesgoClass = "text-danger fw-bold";
    if (riesgo.toLowerCase() === "muy alto") riesgoClass = "text-muy-alto";


    // Mostrar la información
    infoDiv.innerHTML = `
        <div class="card shadow-sm">
            <div class="card-body">
                <h5 class="card-title">🏭 ${opcionSeleccionada.text}</h5>
                <p><strong>Código:</strong> ${codigo}</p>
                <p><strong>Estado:</strong> ${estado}</p>
                <p><strong>Capacidad:</strong> ${capacidad} personas</p>
                <p><strong>Riesgo:</strong> <span class="${riesgoClass}">${riesgo}</span></p>
            </div>
        </div>
    `;
}