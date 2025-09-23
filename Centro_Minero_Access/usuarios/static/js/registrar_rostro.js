// DOM
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startBtn = document.getElementById('startCamera');
const captureBtn = document.getElementById('captureBtn');
const stopBtn = document.getElementById('stopCamera');
const retakeBtn = document.getElementById('retakeBtn');
const overlay = document.getElementById('videoOverlay');
const faceGuide = document.getElementById('faceGuide');
const statusMessage = document.getElementById('statusMessage');

let stream = null;
let capturedImage = null;

function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message status-${type}`;
    statusMessage.style.display = 'block';
    setTimeout(() => { statusMessage.style.display = 'none'; }, 5000);
}

// start camera
startBtn.addEventListener('click', async () => {
    try {
        showStatus('Iniciando cámara...', 'info');
        stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
            audio: false
        });
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            overlay.style.display = 'none';
            faceGuide.style.display = 'block';
            startBtn.style.display = 'none';
            captureBtn.style.display = 'inline-flex';
            stopBtn.style.display = 'inline-flex';
            captureBtn.disabled = false;
            showStatus('Cámara activada. Posicione su rostro y presione Capturar.', 'success');
        };
    } catch (err) {
        console.error('Error cámara:', err);
        showStatus('Error al acceder a la cámara. Revisa permisos.', 'error');
    }
});

// stop camera
stopBtn.addEventListener('click', () => {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
    }
    video.srcObject = null;
    overlay.style.display = 'flex';
    overlay.textContent = '📷 Haga clic en "Activar Cámara" para comenzar';
    faceGuide.style.display = 'none';
    startBtn.style.display = 'inline-flex';
    captureBtn.style.display = 'none';
    stopBtn.style.display = 'none';
    retakeBtn.style.display = 'none';
    captureBtn.disabled = true;
    showStatus('Cámara detenida.', 'info');
});

// capture
captureBtn.addEventListener('click', () => {
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    capturedImage = canvas.toDataURL('image/jpeg', 0.9); // base64
    showStatus('Imagen capturada. Procesando...', 'info');

    captureBtn.style.display = 'none';
    stopBtn.style.display = 'none';
    retakeBtn.style.display = 'inline-flex';

    processImage(capturedImage);
});

// retake
retakeBtn.addEventListener('click', () => {
    retakeBtn.style.display = 'none';
    captureBtn.style.display = 'inline-flex';
    stopBtn.style.display = 'inline-flex';
    showStatus('Listo para capturar nuevamente', 'info');
});

// send to backend
async function processImage(imageBase64) {
    try {
        const resp = await fetch(procesarRostroUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                usuario_id: usuarioId,
                image_data: imageBase64
            })
        });

        const data = await resp.json();

        if (resp.ok && data.success) {
            showStatus(data.message || 'Rostro registrado correctamente', 'success');
            setTimeout(() => { window.location.href = listarUsuariosUrl; }, 2000);
        } else {
            showStatus(data.message || 'Error al procesar rostro', 'error');
            retakeBtn.textContent = '🔄 Intentar Nuevamente';
        }
    } catch (err) {
        console.error('Error procesar imagen:', err);
        showStatus('Error en la petición. Intenta de nuevo.', 'error');
    }
}

// cleanup on unload
window.addEventListener('beforeunload', () => {
    if (stream) stream.getTracks().forEach(t => t.stop());
});
