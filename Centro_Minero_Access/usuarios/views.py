import json
import base64
import logging
import numpy as np
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils.timezone import now

from .models import Usuario, Registro
from .forms import UsuarioForm
from .face_recognition.face_system_opencv import opencv_face_system
from accesos.models import Acceso
from ambientes.models import Ambiente

logger = logging.getLogger(__name__)

# -------------------------
# CRUD de Usuarios
# -------------------------

def listar_usuarios(request):
    usuarios = Usuario.objects.filter(activo=True).order_by("nombre")
    return render(request, "usuarios/listar_usuarios.html", {"usuarios": usuarios})


def crear_usuario(request):
    ambientes = Ambiente.objects.all().order_by('nombre')
    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.activo = False # Inactivo hasta registro facial exitoso
            usuario.face_registered = False
            usuario.save()
            
            form.save_m2m()
            
            if usuario.ambientes_permitidos:
                usuario.migrar_permisos_automaticamente()
            
            messages.success(request, f"✅ Usuario {usuario.nombre} creado exitosamente. Ahora registre su rostro.")
            return redirect("usuarios:registrar_rostro", pk=usuario.pk)
        else:
            messages.error(request, "⚠️ Corrige los errores en el formulario.")
    else:
        form = UsuarioForm()

    return render(request, "usuarios/crear_usuario.html", {"form": form, "ambientes": ambientes})


def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    ambientes = Ambiente.objects.all().order_by('nombre')

    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)

            if usuario.face_image:
                usuario.face_registered = True

            usuario.save()
            
            form.save_m2m()
            
            if usuario.ambientes_permitidos and not usuario.ambientes_directos.exists():
                usuario.migrar_permisos_automaticamente()
            
            messages.success(request, f"✅ Usuario {usuario.nombre} actualizado correctamente.")
            return redirect("usuarios:listar_usuarios")
        else:
            messages.error(request, "⚠️ Corrige los errores en el formulario.")
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, "usuarios/editar_usuario.html", {
        "form": form,
        "usuario": usuario,
        "ambientes": ambientes
    })

def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        nombre = usuario.nombre
        usuario.delete()
        messages.success(request, f'Usuario {nombre} eliminado exitosamente.')
        return redirect('usuarios:listar_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})

def listar_registros(request):
    registros = Registro.objects.all().order_by('-fecha_hora')
    context = {
        'registros': registros
    }
    return render(request, 'usuarios/listar_registros.html', context)

def registrar_rostro(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, "usuarios/registrar_rostro.html", {"usuario": usuario})


# -------------------------
# Endpoints AJAX (Faciales)
# -------------------------

@csrf_protect
@require_http_methods(["POST"])
def procesar_rostro(request):
    try:
        data = json.loads(request.body)
        usuario_id = data.get("usuario_id")
        image_data = data.get("image_data")

        if not usuario_id or not image_data:
            return JsonResponse({"success": False, "message": "Datos incompletos"}, status=400)

        usuario = get_object_or_404(Usuario, pk=usuario_id)
        
        # CAMBIO: Verificar si es un usuario nuevo/inactivo (opcional, para mensaje)
        if not usuario.activo:
            messages.info(request, f"Procesando rostro para activar a {usuario.nombre}...")

        # 1) Encoding facial
        encoding, message = opencv_face_system.encode_face_from_base64(image_data)
        if encoding is None:
            return JsonResponse({"success": False, "message": message or "No se detecto rostro valido"}, status=400)

        # 2) Verificar calidad
        quality_ok, quality_message = opencv_face_system.verify_face_quality(image_data)
        if not quality_ok:
            return JsonResponse({"success": False, "message": quality_message or "Calidad de imagen insuficiente"}, status=400)

        # 3) Guardar imagen facial
        try:
            header, b64data = image_data.split(";base64,")
            ext = header.split("/")[-1]
            file_data = base64.b64decode(b64data)
            # AQUI CAMBIAMOS DE carnet a numero_identificacion
            filename = f"user_{usuario.numero_identificacion}_{usuario.id}.{ext}"
            usuario.face_image.save(filename, ContentFile(file_data), save=False)
        except Exception:
            logger.exception("Error al guardar imagen facial")
            return JsonResponse({"success": False, "message": "Error al guardar imagen"}, status=500)

        # 4) Guardar encoding en formato JSON
        enc_saved = opencv_face_system.save_face_encoding(encoding)
        if isinstance(enc_saved, np.ndarray):
            enc_saved = json.dumps(enc_saved.tolist())

        usuario.face_encoding = enc_saved
        usuario.face_registered = True
        usuario.activo = True # Aqui se activa
        usuario.save()
        
        messages.success(request, f"Usuario {usuario.nombre} activado y rostro registrado exitosamente.")
        return JsonResponse({
            "success": True,
            "message": f"Rostro registrado exitosamente para {usuario.nombre}"
        }, status=200)

    except Exception:
        logger.exception("Error en procesar_rostro")
        return JsonResponse({"success": False, "message": "Error interno del servidor"}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def reconocer_rostro(request):
    try:
        data = json.loads(request.body)
        image_data = data.get("image_data")
        ambiente = data.get("ambiente", "Laboratorio de Sistemas")

        if not image_data:
            return JsonResponse({"success": False, "message": "No se proporcionó imagen"}, status=400)

        usuarios = Usuario.objects.filter(face_registered=True, activo=True)
        if not usuarios.exists():
            return JsonResponse({"success": False, "message": "No hay usuarios registrados"}, status=404)

        user_id, confidence, message = opencv_face_system.recognize_face_from_base64(image_data, usuarios)

        if user_id:
            usuario = get_object_or_404(Usuario, pk=user_id)

            # Alternar Entrada/Salida automáticamente según último registro
            ultimo_registro = Registro.objects.filter(usuario=usuario).order_by("-fecha_hora").first()
            if ultimo_registro and ultimo_registro.tipo == "Entrada":
                tipo_acceso = "Salida"
            else:
                tipo_acceso = "Entrada"

            Registro.objects.create(
                usuario=usuario,
                tipo=tipo_acceso,
                metodo="facial",
                ambiente=ambiente,
                confianza=confidence or 0.0,
                fecha_hora=now()
            )
            
            Acceso.objects.create(
                usuario=usuario,
                ambiente=ambiente,
                metodo='reconocimiento_facial',
                acceso_permitido=True,
                razon_denegacion='Rostro no reconocido'
            )

            return JsonResponse({
                "success": True,
                "message": message,
                "usuario": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    # AQUI CAMBIAMOS DE carnet a numero_identificacion
                    "numero_identificacion": usuario.numero_identificacion,
                    "tipo": usuario.get_tipo_display()
                },
                "confianza": round((confidence or 0) * 100, 1),
                "acceso_autorizado": True,
                "tipo_acceso": tipo_acceso
            }, status=200)

        return JsonResponse({
            "success": False,
            "message": message,
            "acceso_autorizado": False
        }, status=200)

    except Exception:
        logger.exception("Error en reconocer_rostro")
        return JsonResponse({"success": False, "message": "Error interno en el reconocimiento"}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def verificar_camara(request):
    return JsonResponse({"success": True, "message": "Cámara verificada correctamente"}, status=200)