from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from .models import Acceso
from usuarios.models import Usuario, Registro
from ambientes.models import Ambiente, ProtocoloAmbiente  # Importa el modelo Ambiente


def control_acceso_view(request):
    """
    Vista principal de control de acceso.
    - Renderiza la plantilla 'accesos/index.html'.
    - Maneja la lógica de acceso manual por ID (POST).
    """
    
    if request.method == "POST":
        numero_id = request.POST.get('numero_identificacion', '').strip()
        ambiente_nombre = request.POST.get('ambiente', '')  # El nombre del ambiente viene del select
        
        # Validar que el campo no esté vacío
        if not numero_id:
            messages.error(request, '⚠️ Ingrese un número de identificación válido.')
            return redirect('accesos:control_acceso')
        
        try:
            # Buscar usuario activo
            usuario = Usuario.objects.get(numero_identificacion=numero_id, activo=True)
        except Usuario.DoesNotExist:
            messages.error(request, f'❌ Usuario con ID "{numero_id}" no encontrado o inactivo.')
            return redirect('accesos:control_acceso')
        
        try:
            # Obtener el objeto Ambiente
            ambiente = Ambiente.objects.get(nombre=ambiente_nombre)
        except Ambiente.DoesNotExist:
            messages.error(request, f'❌ El ambiente "{ambiente_nombre}" no existe.')
            return redirect('accesos:control_acceso')

        # Verificar permisos
        permisos_raw = usuario.ambientes_permitidos.lower().split(',')
        permisos = [p.strip() for p in permisos_raw if p.strip()]
        
        nombre_ambiente = ambiente.nombre
        
        if 'todos' not in permisos and ambiente_nombre.lower() not in [p.lower() for p in permisos]:
            messages.error(request, f'❌ {usuario.nombre} no tiene permiso para {nombre_ambiente}.')
            return redirect('accesos:control_acceso')
        
        # ÉXITO: Registrar Acceso y Registro
        try:
            # 1. Registro en la tabla Acceso (para el log del sistema)
            Acceso.objects.create(
                usuario=usuario,
                ambiente=ambiente,  # Usamos el objeto Ambiente
                metodo='manual',
                acceso_permitido=True,
                razon_denegacion='',
                confianza=100.0
            )
            
            # 2. Registro en la tabla Registro (para Entrada/Salida)
            ultimo_registro = Registro.objects.filter(usuario=usuario).order_by("-fecha_hora").first()
            tipo_acceso = "Salida" if ultimo_registro and ultimo_registro.tipo == "Entrada" else "Entrada"
            
            Registro.objects.create(
                usuario=usuario,
                tipo=tipo_acceso,
                metodo="manual",
                ambiente=nombre_ambiente,  # Guardamos solo el nombre
                confianza=100.0,
                fecha_hora=datetime.now()
            )
            
            messages.success(request, f'✅ ¡Bienvenido a {nombre_ambiente}, {usuario.nombre}! Acceso registrado como {tipo_acceso}.')
        
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar el acceso: {e}')
        
        # Redireccionar para evitar re-envío del formulario
        return redirect('accesos:control_acceso')
    
    # Lógica para la petición GET (cargar la página inicialmente)
    accesos_lista = Acceso.objects.select_related('usuario', 'ambiente').order_by('-fecha_hora')[:10]
    
    # Obtenemos todos los ambientes para popular el select
    ambientes_list = Ambiente.objects.all()

    context = {
        "accesos_lista": accesos_lista,
        "ambientes_list": ambientes_list
    }
    return render(request, "accesos/index.html", context)


def listar_accesos(request):
    """
    Vista para mostrar la lista completa de accesos.
    """
    accesos = Acceso.objects.select_related('usuario', 'ambiente').all().order_by('-fecha_hora')
    return render(request, "accesos/listar.html", {"accesos": accesos})


# 🔹 Vista para devolver toda la información de un ambiente seleccionado
def ambiente_detalle(request, ambiente_id):
    """
    Devuelve la información completa de un ambiente en formato JSON.
    Incluye resumen de protocolos para mostrar en el frontend.
    """
    try:
        ambiente = Ambiente.objects.get(id=ambiente_id)
        
        # Obtener resumen de protocolos
        resumen_protocolos = ambiente.resumen_protocolos()
        
        data = {
            "id": ambiente.id,
            "nombre": ambiente.nombre,
            "codigo": ambiente.codigo,
            "estado": ambiente.get_estado_display(),  # Texto legible: "Disponible"
            "capacidad": ambiente.capacidad,
            "riesgo": ambiente.get_riesgo_display(),  # Texto legible: "Bajo"
            "riesgo_raw": ambiente.riesgo,  # Valor crudo para clases CSS ('bajo', etc.)
            "protocolos": {
                "total": resumen_protocolos['total'],
                "completados": resumen_protocolos['completados'],
                "pendientes": resumen_protocolos['pendientes'],
                "tareas_pendientes": resumen_protocolos['tareas_pendientes']
            }
        }
        return JsonResponse(data)
    except Ambiente.DoesNotExist:
        return JsonResponse({"error": "Ambiente no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error al obtener detalles: {str(e)}"}, status=500)

        