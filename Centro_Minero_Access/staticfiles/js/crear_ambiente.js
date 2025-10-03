document.addEventListener('DOMContentLoaded', ()=>{
    // Lógica de configuración de tema e idioma
    const overlay=document.getElementById('configOverlay');
    const panel=document.getElementById('configPanel');
    const link=document.getElementById('configLink');
    const close=document.getElementById('closeConfig');
    const cancel=document.getElementById('cancelConfig');
    const save=document.getElementById('saveConfig');
    const theme=document.getElementById('theme');
    const lang=document.getElementById('language');

    function togglePanel(){ panel.classList.toggle('show'); overlay.classList.toggle('show'); }
    function applyTheme(t){ document.body.classList.toggle('dark-mode', t==='dark'); }
    function saveSettings(){
        const s={theme:theme.value,lang:lang.value};
        localStorage.setItem('settings',JSON.stringify(s));
        applyTheme(s.theme);
        togglePanel();
    }
    function load(){
        const s=JSON.parse(localStorage.getItem('settings')||'{}');
        if(s.theme){theme.value=s.theme;applyTheme(s.theme);}
        if(s.lang){lang.value=s.lang;}
    }

    link.addEventListener('click',e=>{e.preventDefault();togglePanel();load();});
    close.addEventListener('click',togglePanel);
    cancel.addEventListener('click',togglePanel);
    save.addEventListener('click',saveSettings);
    overlay.addEventListener('click',togglePanel);
    load();
});
