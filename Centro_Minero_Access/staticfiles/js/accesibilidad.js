// accesibilidad.js - Versión limpia y optimizada
document.addEventListener('DOMContentLoaded', function() {
    applySavedPreferences();
    setTimeout(initializeAccessibilityPanel, 100);
});

function initializeAccessibilityPanel() {
    const btnAccesibilidad = document.getElementById('btnAccesibilidad');
    const menuAccesibilidad = document.getElementById('menuAccesibilidad');

    if (!btnAccesibilidad || !menuAccesibilidad) return;

    btnAccesibilidad.addEventListener('click', function(e) {
        e.stopPropagation();
        const isVisible = menuAccesibilidad.style.display === 'block';
        menuAccesibilidad.style.display = isVisible ? 'none' : 'block';
    });

    document.addEventListener('click', function(e) {
        if (menuAccesibilidad && !menuAccesibilidad.contains(e.target) && e.target !== btnAccesibilidad) {
            menuAccesibilidad.style.display = 'none';
        }
    });

    document.getElementById('contraste').addEventListener('click', toggleHighContrast);
    document.getElementById('aumentarTexto').addEventListener('click', () => changeTextSize(2));
    document.getElementById('disminuirTexto').addEventListener('click', () => changeTextSize(-2));
    document.getElementById('cursorGrande').addEventListener('click', toggleLargeCursor);
    document.getElementById('modoDislexia').addEventListener('click', toggleDyslexiaMode);
    document.getElementById('lectura').addEventListener('click', leerPagina);
    document.getElementById('resetAccesibilidad').addEventListener('click', resetAccessibility);
    document.getElementById('cerrarAccesibilidad').addEventListener('click', () => {
        menuAccesibilidad.style.display = 'none';
    });
}

function toggleHighContrast() {
    const body = document.body;
    const isActive = !body.classList.contains('high-contrast');
    
    body.classList.toggle('high-contrast');
    localStorage.setItem('highContrast', isActive);
    
    const btn = document.getElementById('contraste');
    btn.textContent = isActive ? '🌗 Contraste Normal' : '🌗 Alto Contraste';
    btn.classList.toggle('btn-dark', isActive);
    btn.classList.toggle('btn-outline-dark', !isActive);
    
    forceRepaint();
}

function changeTextSize(change) {
    const body = document.body;
    let currentSize = parseInt(localStorage.getItem('textSize')) || 16;
    let newSize = currentSize + change;
    
    if (newSize < 12) newSize = 12;
    if (newSize > 24) newSize = 24;
    
    body.style.fontSize = newSize + 'px';
    localStorage.setItem('textSize', newSize);
    
    document.getElementById('aumentarTexto').disabled = (newSize >= 24);
    document.getElementById('disminuirTexto').disabled = (newSize <= 12);
    
    forceRepaint();
}

function toggleLargeCursor() {
    const body = document.body;
    const isActive = !body.classList.contains('cursor-grande');
    
    if (isActive) {
        createLargeCursor();
        body.classList.add('cursor-grande');
        localStorage.setItem('cursorGrande', 'true');
        
        const btn = document.getElementById('cursorGrande');
        btn.textContent = '🖱️ Cursor Normal';
        btn.classList.add('btn-warning');
        btn.classList.remove('btn-outline-warning');
    } else {
        removeLargeCursor();
        body.classList.remove('cursor-grande');
        localStorage.setItem('cursorGrande', 'false');
        
        const btn = document.getElementById('cursorGrande');
        btn.textContent = '🖱️ Cursor Grande';
        btn.classList.remove('btn-warning');
        btn.classList.add('btn-outline-warning');
    }
    
    forceRepaint();
}

function toggleDyslexiaMode() {
    const body = document.body;
    const isActive = !body.classList.contains('modo-dislexia');
    
    body.classList.toggle('modo-dislexia');
    localStorage.setItem('modoDislexia', isActive);
    
    const btn = document.getElementById('modoDislexia');
    btn.textContent = isActive ? '📘 Fuente Normal' : '📘 Fuente Dislexia';
    btn.classList.toggle('btn-info', isActive);
    btn.classList.toggle('btn-outline-info', !isActive);
    
    forceRepaint();
}

function leerPagina() {
    const mainContent = document.querySelector('main') || document.body;
    let texto = '';
    
    const elementosTexto = mainContent.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, td, th, .card, .alert');
    elementosTexto.forEach(el => {
        if (el.offsetParent !== null && el.textContent.trim().length > 0) {
            texto += el.textContent.trim() + '. ';
        }
    });

    if (!texto) texto = document.body.innerText;

    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(texto);
        utterance.lang = 'es-ES';
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;

        speechSynthesis.speak(utterance);
        
        // Guardar referencia para poder detener
        window.lecturaActual = utterance;
        
    } else {
        alert('Tu navegador no soporta la función de lectura en voz alta.');
    }
}

// FUNCIÓN PARA DETENER LA LECTURA
function detenerLectura() {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
        console.log('Lectura detenida');
    }
}

// Función para alternar entre leer y detener
function toggleLectura() {
    const boton = document.getElementById('botonLectura');
    
    if (speechSynthesis.speaking) {
        // Si está hablando, detener
        speechSynthesis.cancel();
        boton.innerHTML = '<i class="bi bi-play-circle"></i> Leer Página';
        boton.style.background = '#008037';
    } else {
        // Si no está hablando, empezar a leer
        leerPagina();
        boton.innerHTML = '<i class="bi bi-stop-circle"></i> Detener';
        boton.style.background = '#dc3545';
        
        // Cuando termine la lectura, volver al estado original
        const verificarFin = setInterval(() => {
            if (!speechSynthesis.speaking) {
                boton.innerHTML = '<i class="bi bi-play-circle"></i> Leer Página';
                boton.style.background = '#008037';
                clearInterval(verificarFin);
            }
        }, 500);
    }
}

function resetAccessibility() {
    const body = document.body;
    
    removeLargeCursor();
    
    body.classList.remove('high-contrast', 'modo-dislexia', 'cursor-grande');
    body.style.fontSize = '';
    
    localStorage.removeItem('highContrast');
    localStorage.removeItem('textSize');
    localStorage.removeItem('cursorGrande');
    localStorage.removeItem('modoDislexia');
    
    const buttons = {
        'contraste': ['🌗 Alto Contraste', 'btn-outline-dark'],
        'cursorGrande': ['🖱️ Cursor Grande', 'btn-outline-warning'],
        'modoDislexia': ['📘 Fuente Dislexia', 'btn-outline-info'],
        'lectura': ['🔊 Leer Página', 'btn-outline-success']
    };
    
    Object.entries(buttons).forEach(([id, [text, className]]) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.innerHTML = text;
            btn.className = `btn ${className} w-100 mb-2`;
        }
    });
    
    document.getElementById('aumentarTexto').disabled = false;
    document.getElementById('disminuirTexto').disabled = false;
    
    speechSynthesis.cancel();
    
    alert('Configuración de accesibilidad restablecida');
}

function applySavedPreferences() {
    const body = document.body;
    
    setTimeout(() => {
        if (localStorage.getItem('highContrast') === 'true') {
            body.classList.add('high-contrast');
            const btn = document.getElementById('contraste');
            if (btn) {
                btn.textContent = '🌗 Contraste Normal';
                btn.classList.add('btn-dark');
                btn.classList.remove('btn-outline-dark');
            }
        }
        
        const savedSize = localStorage.getItem('textSize');
        if (savedSize) {
            body.style.fontSize = savedSize + 'px';
            
            const aumentarBtn = document.getElementById('aumentarTexto');
            const disminuirBtn = document.getElementById('disminuirTexto');
            if (aumentarBtn && disminuirBtn) {
                aumentarBtn.disabled = (parseInt(savedSize) >= 24);
                disminuirBtn.disabled = (parseInt(savedSize) <= 12);
            }
        }
        
        if (localStorage.getItem('cursorGrande') === 'true') {
            createLargeCursor();
            body.classList.add('cursor-grande');
            const btn = document.getElementById('cursorGrande');
            if (btn) {
                btn.textContent = '🖱️ Cursor Normal';
                btn.classList.add('btn-warning');
                btn.classList.remove('btn-outline-warning');
            }
        }
        
        if (localStorage.getItem('modoDislexia') === 'true') {
            body.classList.add('modo-dislexia');
            const btn = document.getElementById('modoDislexia');
            if (btn) {
                btn.textContent = '📘 Fuente Normal';
                btn.classList.add('btn-info');
                btn.classList.remove('btn-outline-info');
            }
        }
    }, 50);
}

function createLargeCursor() {
    removeLargeCursor();
    
    const cursor = document.createElement('div');
    cursor.id = 'custom-large-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 30px;
        height: 30px;
        background: rgba(0, 123, 255, 0.7);
        border: 2px solid white;
        border-radius: 50%;
        pointer-events: none;
        z-index: 999999;
        transform: translate(-50%, -50%);
        transition: transform 0.1s ease;
        box-shadow: 0 0 10px rgba(0, 123, 255, 0.5);
    `;
    
    const dot = document.createElement('div');
    dot.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        width: 6px;
        height: 6px;
        background: white;
        border-radius: 50%;
        transform: translate(-50%, -50%);
    `;
    
    cursor.appendChild(dot);
    document.body.appendChild(cursor);
    
    document.addEventListener('mousemove', moveCustomCursor);
    
    document.addEventListener('mouseover', function(e) {
        if (e.target.matches('button, a, [onclick], [role="button"], input, select, textarea')) {
            cursor.style.background = 'rgba(40, 167, 69, 0.8)';
            cursor.style.transform = 'translate(-50%, -50%) scale(1.2)';
        }
    });
    
    document.addEventListener('mouseout', function(e) {
        if (e.target.matches('button, a, [onclick], [role="button"], input, select, textarea')) {
            cursor.style.background = 'rgba(0, 123, 255, 0.7)';
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
        }
    });
    
    document.body.style.cursor = 'none';
}

function moveCustomCursor(e) {
    const cursor = document.getElementById('custom-large-cursor');
    if (cursor) {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    }
}

function removeLargeCursor() {
    const cursor = document.getElementById('custom-large-cursor');
    if (cursor) {
        cursor.remove();
    }
    
    document.removeEventListener('mousemove', moveCustomCursor);
    document.body.style.cursor = '';
}

function forceRepaint() {
    const body = document.body;
    body.style.display = 'none';
    body.offsetHeight;
    body.style.display = '';
}




