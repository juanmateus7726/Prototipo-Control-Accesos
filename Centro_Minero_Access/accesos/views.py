from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from datetime import datetime
from .models import Acceso
from usuarios.models import Usuario, Registro  # Para registrar también en Registro


def index(request):
    """
    Vista principal: Renderiza index.html y maneja POST para acceso manual por ID.
    Verifica usuario, permisos, registra Acceso y Registro, muestra mensaje "Bienvenido".
    """
    # Accesos recientes (últimos 10)
    accesos_lista = Acceso.objects.select_related('usuario').all()[:10]
    
    if request.method == "POST":
        numero_id = request.POST.get('numero_identificacion', '').strip()
        ambiente_codigo = request.POST.get('ambiente', 'sistemas')  # Del select
        
        if not numero_id:
            messages.error(request, '⚠️ Ingrese un número de identificación válido.')
        else:
            # Buscar usuario por numero_identificacion (solo activos)
            try:
                usuario = Usuario.objects.get(numero_identificacion=numero_id, activo=True)
            except Usuario.DoesNotExist:
                messages.error(request, f'❌ Usuario con ID "{numero_id}" no encontrado o inactivo.')
                return render(request, "accesos/index.html", {"accesos_lista": accesos_lista})
            
            # Verificar permisos por ambiente (simple: split de ambientes_permitidos)
            permisos = usuario.ambientes_permitidos.lower().split(',')
            permisos_limpios = [p.strip() for p in permisos if p.strip()]
            if 'todos' not in permisos_limpios and ambiente_codigo not in permisos_limpios:
                # Obtener nombre del ambiente para mensaje
                nombre_ambiente = dict(Acceso.AMBIENTE_CHOICES).get(ambiente_codigo, 'desconocido')
                messages.error(request, f'❌ {usuario.nombre} no tiene permiso para {nombre_ambiente}.')
                return render(request, "accesos/index.html", {"accesos_lista": accesos_lista})
            
            # ÉXITO: Registrar acceso
            nombre_ambiente = dict(Acceso.AMBIENTE_CHOICES).get(ambiente_codigo, 'el ambiente')
            # 1. En Acceso (accesos)
            Acceso.objects.create(
                usuario=usuario,
                ambiente=ambiente_codigo,
                metodo='manual',
                acceso_permitido=True,
                razon_denegacion='',  # Vacío si OK
                confianza=100.0  # 100% para manual
            )
            
            # 2. En Registro (usuarios) – alterna Entrada/Salida como en facial
            ultimo_registro = Registro.objects.filter(usuario=usuario).order_by("-fecha_hora").first()
            tipo_acceso = "Salida" if ultimo_registro and ultimo_registro.tipo == "Entrada" else "Entrada"
            Registro.objects.create(
                usuario=usuario,
                tipo=tipo_acceso,
                metodo="manual",
                ambiente=nombre_ambiente,  # Nombre legible
                confianza=100.0,
                fecha_hora=datetime.now()
            )
            
            # Mensaje bienvenida
            nombre_ambiente = dict(Acceso.AMBIENTE_CHOICES).get(ambiente_codigo, 'el ambiente')
            messages.success(request, f'✅ ¡Bienvenido al {nombre_ambiente}, {usuario.nombre}! Acceso registrado como {tipo_acceso}.')
            
            # Actualizar lista reciente
            accesos_lista = Acceso.objects.select_related('usuario').all()[:10]
        
        # Redirige a sí misma para mostrar messages y tabla actualizada
        return render(request, "accesos/index.html", {"accesos_lista": accesos_lista})
    
    # GET: Solo renderiza
    return render(request, "accesos/index.html", {"accesos_lista": accesos_lista})


# Opcional: Mantén si lo usas para otros forms
def registrar_acceso(request):
    # ... (tu código viejo, pero no lo usamos para manual)
    return redirect("accesos:index")


def listar_accesos(request):
    accesos = Acceso.objects.select_related('usuario').all()
    return render(request, "accesos/listar.html", {"accesos": accesos})
