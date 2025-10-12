// responsive_global.js - Versión MEJORADA que SÍ funciona
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para asegurar que el DOM esté completamente cargado
    setTimeout(initializeResponsiveFeatures, 100);
});

function initializeResponsiveFeatures() {
    // 1. PRIMERO buscar sidebars existentes
    const sidebars = document.querySelectorAll('.sidebar');
    
    if (sidebars.length > 0 && window.innerWidth <= 767) {
        console.log('📱 Inicializando sidebars existentes...');
        sidebars.forEach((sidebar, index) => {
            initializeSidebar(sidebar, index);
        });
    } 
    // 2. SI NO HAY SIDEBARS, convertir header en sidebar
    else if (window.innerWidth <= 767) {
        console.log('📱 Convirtiendo header en sidebar...');
        convertHeaderToSidebar();
    }
    
    // 3. INICIALIZAR TABLAS RESPONSIVAS
    initializeResponsiveTables();
}

function initializeSidebar(sidebar, index) {
    const sidebarId = `sidebar-${index}`;
    sidebar.id = sidebarId;
    
    // Crear botón hamburguesa
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'mobile-menu-toggle';
    toggleBtn.innerHTML = '☰';
    toggleBtn.setAttribute('aria-label', 'Abrir menú');
    
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.className = 'mobile-sidebar-overlay';
    
    // Insertar elementos en el DOM
    document.body.appendChild(toggleBtn);
    document.body.appendChild(overlay);
    
    // Asegurar que el sidebar tenga los estilos básicos
    if (!sidebar.style.background) {
        sidebar.style.background = 'linear-gradient(180deg, #008037, #00a84f)';
    }
    
    // EVENTOS
    toggleBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        console.log('🎯 Sidebar toggled:', sidebar.classList.contains('active'));
    });
    
    overlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    });
    
    // Cerrar al hacer clic en links del sidebar
    const sidebarLinks = sidebar.querySelectorAll('a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Solo cerrar si es un link interno (no externo)
            if (!this.href || this.href.includes('javascript') || this.getAttribute('onclick')) {
                return;
            }
            
            setTimeout(() => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }, 300);
        });
    });
    
    // Cerrar al presionar ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });
    
    console.log(`✅ Sidebar ${index} inicializado correctamente`);
}

function initializeResponsiveTables() {
    // Hacer tablas responsivas
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive-mobile')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-container';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Re-inicializar cuando cambie el tamaño de la ventana
let resizeTimeout;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (window.innerWidth <= 767) {
            initializeResponsiveFeatures();
        } else {
            // Limpiar elementos móviles en desktop
            document.querySelectorAll('.mobile-menu-toggle, .mobile-sidebar-overlay').forEach(el => {
                el.remove();
            });
        }
    }, 250);
});





// NUEVA FUNCIÓN: Convertir header horizontal en sidebar
function convertHeaderToSidebar() {
    const topHeaders = document.querySelectorAll('.top-header');
    
    topHeaders.forEach((header, index) => {
        // Verificar si ya se convirtió
        if (document.getElementById(`converted-sidebar-${index}`)) {
            return;
        }
        
        // Crear nuevo sidebar a partir del header
        const convertedSidebar = document.createElement('aside');
        convertedSidebar.className = 'header-converted-sidebar';
        convertedSidebar.id = `converted-sidebar-${index}`;
        
        // Obtener logo del header
        const logo = header.querySelector('.logo');
        const navBar = header.querySelector('.nav-bar');
        
        if (logo) {
            const convertedLogo = document.createElement('div');
            convertedLogo.className = 'converted-logo';
            
            // Copiar contenido del logo
            const brandTitle = logo.querySelector('#brandTitle, .brand span:first-child');
            const brandSubtitle = logo.querySelector('#brandSubtitle, .brand span:last-child');
            
            if (brandTitle) {
                convertedLogo.innerHTML = `
                    <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">⚙️</div>
                    <div>${brandTitle.textContent || 'SENA'}</div>
                    ${brandSubtitle ? `<div style="font-size: 0.9rem; opacity: 0.8;">${brandSubtitle.textContent}</div>` : ''}
                `;
            } else {
                convertedLogo.innerHTML = `
                    <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">⚙️</div>
                    <div>Sistema SENA</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Control de Accesos</div>
                `;
            }
            
            convertedSidebar.appendChild(convertedLogo);
        }
        
        // Obtener navegación del header
        if (navBar) {
            const convertedNav = document.createElement('nav');
            convertedNav.className = 'converted-nav';
            
            // Copiar links de navegación (excluir configuración)
            const navLinks = navBar.querySelectorAll('a.nav-link:not(#configLink)');
            navLinks.forEach(link => {
                const clonedLink = link.cloneNode(true);
                clonedLink.style.display = 'flex'; // Asegurar que sea visible
                convertedNav.appendChild(clonedLink);
            });
            
            // Agregar link de configuración al final si existe
            const configLink = navBar.querySelector('#configLink');
            if (configLink) {
                const clonedConfigLink = configLink.cloneNode(true);
                clonedConfigLink.style.display = 'flex';
                convertedNav.appendChild(clonedConfigLink);
            }
            
            convertedSidebar.appendChild(convertedNav);
        }
        
        // Agregar sidebar convertido al body
        document.body.appendChild(convertedSidebar);
        document.body.classList.add('has-converted-sidebar');
        
        // Inicializar el sidebar convertido
        initializeSidebar(convertedSidebar, index + 100); // ID alto para diferenciar
        
        console.log(`✅ Header convertido a sidebar ${index}`);
    });
}