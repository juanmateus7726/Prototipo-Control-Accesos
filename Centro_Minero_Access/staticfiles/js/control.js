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