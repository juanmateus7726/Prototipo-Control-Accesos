// =====================
// ACCESIBILIDAD SENA - MÓDULO COMPLETO
// =====================

// Elementos principales
const btn = document.getElementById('btnAccesibilidad');
const menu = document.getElementById('menuAccesibilidad');
const cerrar = document.getElementById('cerrarAccesibilidad');

// Mostrar / ocultar menú flotante
if (btn && menu && cerrar) {
    btn.addEventListener('click', () => {
        menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
    });

    cerrar.addEventListener('click', () => {
        menu.style.display = 'none';
    });
}

// =====================
// 🔹 CONTRASTE ALTO
// =====================
const contraste = document.getElementById('contraste');
if (contraste) {
    contraste.addEventListener('click', () => {
        document.body.classList.toggle('alto-contraste');
        localStorage.setItem('altoContraste', document.body.classList.contains('alto-contraste'));
    });

    // Mantener preferencia al recargar
    if (localStorage.getItem('altoContraste') === 'true') {
        document.body.classList.add('alto-contraste');
    }
}

// =====================
// 🔹 TAMAÑO DE TEXTO
// =====================
let tamañoBase = parseInt(localStorage.getItem('tamanoTexto')) || 100;

document.body.style.fontSize = tamañoBase + '%';

const btnAumentar = document.getElementById('aumentarTexto');
const btnDisminuir = document.getElementById('disminuirTexto');
const btnResetTexto = document.getElementById('resetTexto');

if (btnAumentar) {
    btnAumentar.addEventListener('click', () => {
        tamañoBase = Math.min(200, tamañoBase + 10);
        document.body.style.fontSize = tamañoBase + '%';
        localStorage.setItem('tamanoTexto', tamañoBase);
    });
}

if (btnDisminuir) {
    btnDisminuir.addEventListener('click', () => {
        tamañoBase = Math.max(80, tamañoBase - 10);
        document.body.style.fontSize = tamañoBase + '%';
        localStorage.setItem('tamanoTexto', tamañoBase);
    });
}

if (btnResetTexto) {
    btnResetTexto.addEventListener('click', () => {
        tamañoBase = 100;
        document.body.style.fontSize = tamañoBase + '%';
        localStorage.setItem('tamanoTexto', tamañoBase);
    });
}

// =====================
// 🔹 LECTURA EN VOZ ALTA
// =====================
const lectura = document.getElementById('lectura');
let leyendo = false;

if (lectura) {
    lectura.addEventListener('click', () => {
        if (!leyendo) {
            const texto = document.body.innerText;
            const speech = new SpeechSynthesisUtterance(texto);
            speech.lang = 'es-ES';
            speech.rate = 1;
            speech.pitch = 1;
            window.speechSynthesis.speak(speech);
            leyendo = true;
            lectura.innerText = '🛑 Detener lectura';
        } else {
            window.speechSynthesis.cancel();
            leyendo = false;
            lectura.innerText = '🔊 Leer página';
        }
    });
}

// =====================
// 🔹 CURSOR GRANDE
// =====================
const cursorBtn = document.getElementById('cursorGrande');
if (cursorBtn) {
    cursorBtn.addEventListener('click', () => {
        document.body.classList.toggle('cursor-grande');
        localStorage.setItem('cursorGrande', document.body.classList.contains('cursor-grande'));
    });

    // Persistencia
    if (localStorage.getItem('cursorGrande') === 'true') {
        document.body.classList.add('cursor-grande');
    }
}

// =====================
// 🔹 MODO DISLEXIA (fuente amigable)
// =====================
const dislexiaBtn = document.getElementById('modoDislexia');
if (dislexiaBtn) {
    dislexiaBtn.addEventListener('click', () => {
        document.body.classList.toggle('modo-dislexia');
        localStorage.setItem('modoDislexia', document.body.classList.contains('modo-dislexia'));
    });

    if (localStorage.getItem('modoDislexia') === 'true') {
        document.body.classList.add('modo-dislexia');
    }
}

// =====================
// 🔹 RESTABLECER TODO
// =====================
const resetAll = document.getElementById('resetAccesibilidad');
if (resetAll) {
    resetAll.addEventListener('click', () => {
        localStorage.clear();
        document.body.classList.remove('alto-contraste', 'cursor-grande', 'modo-dislexia');
        document.body.style.fontSize = '100%';
        alert('♻️ Preferencias de accesibilidad restablecidas.');
        location.reload();
    });
}
