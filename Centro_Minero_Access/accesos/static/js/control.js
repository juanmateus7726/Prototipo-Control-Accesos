/* =========================
   BASE DE DATOS SIMULADA
   ========================= */
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
        protocolo: "⚠️ OBLIGATORIO: Usar bata, gafas de seguridad y guantes. Prohibido ingresar con comida o bebidas.",
        riesgo: "alto"
    },
    carbones: {
        nombre: "Laboratorio de Carbones",
        protocolo: "⚠️ Usar mascarilla N95 y ropa de trabajo. Ventilación obligatoria.",
        riesgo: "alto"
    },
    biotecnologia: {
        nombre: "Laboratorio de Biotecnología",
        protocolo: "⚠️ Esterilizar manos, usar bata estéril y gorro.",
        riesgo: "medio"
    },
    beneficios: {
        nombre: "Lab. Beneficios Minerales",
        protocolo: "⚠️ Casco, gafas, calzado y guantes. Verificar equipos antes del uso.",
        riesgo: "alto"
    },
    sistemas: {
        nombre: "Laboratorio de Sistemas",
        protocolo: "💻 No ingresar líquidos. Usar credenciales de red asignadas.",
        riesgo: "bajo"
    },
    abc_maquinaria: {
        nombre: "Ambiente ABC - Maquinaria Pesada",
        protocolo: "🚨 Casco, botas, chaleco reflectivo y gafas OBLIGATORIOS.",
        riesgo: "muy_alto"
    },
    minas_didacticas: {
        nombre: "Minas Didácticas",
        protocolo: "🚨 Casco minero, botas, lámpara y detector de gases OBLIGATORIOS.",
        riesgo: "muy_alto"
    },
    bilinguismo: {
        nombre: "Ambiente de Bilingüismo",
        protocolo: "ℹ️ Mantener silencio y orden.",
        riesgo: "bajo"
    }
};

/* =========================
   VARIABLES GLOBALES
   ========================= */
let ambienteActual = "sistemas";
let cameraActive = false;
let stream = null;

/* =========================
   FUNCIONES DE INTERFAZ
   ========================= */
function cargarUsuariosPrueba() {
    const grid = document.getElementById("usersGrid");
    if (!grid) return;
    grid.innerHTML = "";

    Object.entries(usuarios).forEach(([carnet, user]) => {
        const userCard = document.createElement("div");
        userCard.className = `user-card ${user.tipo}`;
        userCard.onclick = () => probarUsuarioDesdeGrid(carnet);

        const estado = user.activo ? "✅" : "❌";
        const areas = user.areas_permitidas.includes("todos")
            ? "Todas"
            : user.areas_permitidas.join(", ");

        userCard.innerHTML = `
            <div style="font-weight:600;color:#2c3e50;">${estado} ${user.nombre}</div>
            <div style="color:#7f8c8d;font-size:.9rem;">🎫 ${carnet}</div>
            <div style="color:#7f8c8d;font-size:.9rem;">👤 ${user.tipo}</div>
            <div style="color:#7f8c8d;font-size:.8rem;">📍 ${areas}</div>
            <div style="margin-top:8px;">
                <small style="color:#3498db;cursor:pointer;">👆 Seleccionar</small>
            </div>
        `;
        grid.appendChild(userCard);
    });
}

function probarUsuarioDesdeGrid(carnet) {
    const select = document.getElementById("id_usuario");
    if (select) {
        select.value = carnet;
        select.dispatchEvent(new Event("change"));
    }
    verificarAcceso(carnet, "seleccion_manual");
}

/* =========================
   AMBIENTE Y PROTOCOLO
   ========================= */
function cambiarAmbiente() {
    const select = document.getElementById("ambienteSelect");
    if (select) {
        ambienteActual = select.value;
        actualizarInfoAmbiente();
        agregarLog(`📍 Ambiente cambiado a: ${ambientes[ambienteActual].nombre}`);
    }
}

function actualizarInfoAmbiente() {
    const ambiente = ambientes[ambienteActual];
    const info = document.getElementById("ambienteInfo");
    if (!info) return;
    info.innerHTML = `
        ${ambiente.nombre}
        <span class="risk-indicator risk-${ambiente.riesgo}">
            Riesgo: ${ambiente.riesgo.replace("_", " ")}
        </span>
    `;
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
function verificarAcceso(carnet, metodo) {
    if (!usuarios[carnet]) {
        return denegarAcceso("Usuario no registrado", carnet, metodo);
    }
    const user = usuarios[carnet];
    if (!user.activo) {
        return denegarAcceso("Usuario inactivo", carnet, metodo);
    }
    if (!user.areas_permitidas.includes("todos") &&
        !user.areas_permitidas.includes(ambienteActual)) {
        return denegarAcceso("Sin permiso para este ambiente", carnet, metodo);
    }
    permitirAcceso(user, carnet, metodo);
}

function permitirAcceso(user, carnet, metodo) {
    const ts = new Date().toLocaleTimeString();
    const ambiente = ambientes[ambienteActual];
    const status = document.getElementById("statusIndicator");
    const info = document.getElementById("userInfo");

    if (status) {
        status.className = "status-indicator status-granted";
        status.innerHTML = "🟢 ACCESO PERMITIDO<br><small>¡Bienvenido!</small>";
    }
    if (info) {
        info.innerHTML = `
            <div style="background:rgba(46,204,113,0.1);padding:15px;border-radius:10px;">
                <strong>👤 Usuario:</strong> ${user.nombre}<br>
                <strong>🎫 Carnet:</strong> ${carnet}<br>
                <strong>Tipo:</strong> ${user.tipo}<br>
                <strong>Ambiente:</strong> ${ambiente.nombre}<br>
                <strong>Hora:</strong> ${ts}<br>
                <strong>Método:</strong> ${metodo}
            </div>
        `;
    }
    agregarLog(`✅ ${ts} - Acceso permitido a ${user.nombre}`);
    setTimeout(resetearEstado, 8000);
}

function denegarAcceso(razon, carnet, metodo) {
    const ts = new Date().toLocaleTimeString();
    const status = document.getElementById("statusIndicator");
    const info = document.getElementById("userInfo");

    if (status) {
        status.className = "status-indicator status-denied";
        status.innerHTML = `🔴 ACCESO DENEGADO<br><small>${razon}</small>`;
    }
    if (info) {
        info.innerHTML = `
            <div style="background:rgba(231,76,60,0.1);padding:15px;border-radius:10px;">
                ❌ Acceso Denegado<br>
                🎫 Carnet: ${carnet}<br>
                ⚠️ Razón: ${razon}<br>
                ⏰ Hora: ${ts}<br>
                🔍 Método: ${metodo}
            </div>
        `;
    }
    agregarLog(`❌ ${ts} - Acceso denegado: ${razon}`);
    setTimeout(resetearEstado, 5000);
}

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
    cargarUsuariosPrueba();
    actualizarInfoAmbiente();

    // Enlace select de usuario con botones .user-btn
    const usuarioSelect = document.getElementById("id_usuario");
    document.querySelectorAll(".user-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            if (usuarioSelect) {
                usuarioSelect.value = id;
                usuarioSelect.dispatchEvent(new Event("change"));
            }
        });
    });

    // Validar formulario
    const form = document.getElementById("accesoForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            const u = document.getElementById("id_usuario")?.value;
            const amb = document.getElementById("laboratorio-select")?.value;
            const met = document.getElementById("metodo-select")?.value;
            if (!u || !amb || !met) {
                e.preventDefault();
                alert("Completa todos los campos");
            }
        });
    }
});