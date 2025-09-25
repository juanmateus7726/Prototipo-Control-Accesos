from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from .models import Acceso
from usuarios.models import Usuario, Registro
from ambientes.models import Ambiente, ProtocoloAmbiente

def control_acceso_view(request):
    """
    Vista principal de control de acceso con sistema dual de permisos.
    """
    
    if request.method == "POST":
        numero_id = request.POST.get('numero_identificacion', '').strip()
        ambiente_id = request.POST.get('ambiente_id', '')
        
        if not numero_id or not ambiente_id:
            messages.error(request, '⚠️ Complete todos los campos.')
            return redirect('accesos:control_acceso')
        
        try:
            usuario = Usuario.objects.get(numero_identificacion=numero_id, activo=True)
            ambiente = Ambiente.objects.get(id=ambiente_id)
        except Usuario.DoesNotExist:
            messages.error(request, f'❌ Usuario con ID "{numero_id}" no encontrado o inactivo.')
            return redirect('accesos:control_acceso')
        except Ambiente.DoesNotExist:
            messages.error(request, f'❌ Ambiente no encontrado.')
            return redirect('accesos:control_acceso')

        # VERIFICACIÓN DE PERMISOS
        if not usuario.tiene_permiso_ambiente(ambiente):
            messages.error(request, f'❌ {usuario.nombre} no tiene permiso para {ambiente.nombre}.')
            return redirect('accesos:control_acceso')
        
        # Migración automática en el primer acceso exitoso
        try:
            usuario.migrar_permisos_automaticamente()
        except Exception as e:
            print(f"Error en migración automática: {e}")
            # Continuar aunque falle la migración
        
        # REGISTRAR ACCESO
        try:
            # 1. Registro en la tabla Acceso
            Acceso.objects.create(
                usuario=usuario,
                ambiente=ambiente,
                metodo='manual',
                acceso_permitido=True,
                razon_denegacion='',
                confianza=100.0
            )
            
            # 2. Determinar tipo de acceso (Entrada/Salida)
            ultimo_registro = Registro.objects.filter(usuario=usuario).order_by("-fecha_hora").first()
            tipo_acceso = "Salida" if ultimo_registro and ultimo_registro.tipo == "Entrada" else "Entrada"
            
            # 3. Registro en la tabla Registro
            Registro.objects.create(
                usuario=usuario,
                tipo=tipo_acceso,
                metodo="manual",
                ambiente=ambiente.nombre,
                confianza=100.0,
                fecha_hora=datetime.now()
            )
            
            messages.success(request, f'✅ ¡Bienvenido a {ambiente.nombre}, {usuario.nombre}! Acceso registrado como {tipo_acceso}.')
        
        except Exception as e:
            messages.error(request, f'❌ Ocurrió un error al registrar el acceso: {e}')
        
        return redirect('accesos:control_acceso')
    
    # GET request - Mostrar página
    accesos_lista = Acceso.objects.select_related('usuario', 'ambiente').order_by('-fecha_hora')[:10]
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

def ambiente_detalle(request, ambiente_id):
    """
    Devuelve la información completa de un ambiente en formato JSON.
    """
    try:
        ambiente = Ambiente.objects.get(id=ambiente_id)
        
        # Obtener resumen de protocolos
        resumen_protocolos = ambiente.resumen_protocolos()
        
        data = {
            "id": ambiente.id,
            "nombre": ambiente.nombre,
            "codigo": ambiente.codigo,
            "estado": ambiente.get_estado_display(),
            "capacidad": ambiente.capacidad,
            "riesgo": ambiente.get_riesgo_display(),
            "riesgo_raw": ambiente.riesgo,
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