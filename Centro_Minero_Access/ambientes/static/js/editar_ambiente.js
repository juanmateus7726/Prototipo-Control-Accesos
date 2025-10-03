document.addEventListener("DOMContentLoaded", ()=>{
            const overlay=document.getElementById("configOverlay"),
                panel=document.getElementById("configPanel"),
                link=document.getElementById("configLink"),
                close=document.getElementById("closeConfig"),
                cancel=document.getElementById("cancelConfig"),
                save=document.getElementById("saveConfig"),
                themeSel=document.getElementById("theme"),
                langSel=document.getElementById("language");

            const texts={
                es:{title:"✍️ Editar Ambiente",save:"💾 Guardar Cambios",back:"⬅ Volver a la lista"},
                en:{title:"✍️ Edit Room",save:"💾 Save Changes",back:"⬅ Back to list"}
            };

            function open(){panel.classList.add("show");overlay.classList.add("show");}
            function closeAll(){panel.classList.remove("show");overlay.classList.remove("show");}
            function load(){
                let s=JSON.parse(localStorage.getItem("settings")||"{}");
                themeSel.value=s.theme||"light";
                langSel.value=s.lang||"es";
                applyTheme(s.theme||"light");
                applyLang(s.lang||"es");
            }
            function saveSet(){
                localStorage.setItem("settings",JSON.stringify({theme:themeSel.value,lang:langSel.value}));
                applyTheme(themeSel.value);applyLang(langSel.value);closeAll();
            }
            function applyTheme(t){document.body.classList.toggle("dark-mode",t==="dark");}
            function applyLang(l){
                const tx=texts[l]||texts.es;
                document.getElementById("pageTitle").textContent=tx.title;
                document.getElementById("btnSave").textContent=tx.save;
                const backLink = document.querySelector('.back-link');
                if (backLink) {
                    backLink.textContent = tx.back;
                }
            }
            link.addEventListener("click",e=>{e.preventDefault();load();open();});
            overlay.addEventListener("click",closeAll);
            close.addEventListener("click",closeAll);
            cancel.addEventListener("click",closeAll);
            save.addEventListener("click",saveSet);
            load();
        });