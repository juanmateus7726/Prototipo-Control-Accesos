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
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


# =========================================================
# 🔹 LISTAR USUARIOS
# =========================================================
@login_required
def listar_usuarios(request):
    """
    Lista los usuarios activos.
    """
    usuarios = Usuario.objects.filter(activo=True).order_by("nombre")
    return render(request, "usuarios/listar_usuarios.html", {"usuarios": usuarios})

@login_required
def listar_usuarios_deshabilitados(request):
    """
    Lista los usuarios deshabilitados (inactivos).
    """
    usuarios = Usuario.objects.filter(activo=False).order_by("nombre")
    return render(request, "usuarios/listar_usuarios_deshabilitados.html", {"usuarios": usuarios})


# =========================================================
# 🔹 CRUD USUARIOS
# =========================================================
@login_required
def crear_usuario(request):
    ambientes = Ambiente.objects.all().order_by('nombre')
    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.activo = False  # Inactivo hasta registro facial exitoso
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

@login_required
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

@login_required
def eliminar_usuario(request, pk):
    """
    ⚠️ Eliminación permanente del usuario.
    Se mantiene por compatibilidad, pero recomendamos usar deshabilitar_usuario().
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        nombre = usuario.nombre
        usuario.delete()
        messages.success(request, f'Usuario {nombre} eliminado exitosamente.')
        return redirect('usuarios:listar_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})


# =========================================================
# 🔹 DESHABILITAR / REACTIVAR USUARIOS (Soft Delete)
# =========================================================
@login_required
def deshabilitar_usuario(request, pk):
    """
    Deshabilita un usuario (soft delete), sin borrar sus datos ni registros.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.activo = False
        usuario.save()
        messages.success(request, f"🚫 El usuario '{usuario.nombre}' fue deshabilitado correctamente.")
        return redirect('usuarios:listar_usuarios')

    return render(request, 'usuarios/deshabilitar_usuario.html', {'usuario': usuario})

@login_required
def reactivar_usuario(request, pk):
    """
    Reactiva un usuario previamente deshabilitado.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.activo = True
        usuario.save()
        messages.success(request, f"✅ El usuario '{usuario.nombre}' fue reactivado correctamente.")
        return redirect('usuarios:listar_usuarios_deshabilitados')

    return render(request, 'usuarios/reactivar_usuario.html', {'usuario': usuario})


# =========================================================
# 🔹 REGISTROS DE ACCESO
# =========================================================
@login_required
def listar_registros(request):
    registros = Registro.objects.all().order_by('-fecha_hora')
    return render(request, 'usuarios/listar_registros.html', {'registros': registros})

@login_required
def registrar_rostro(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, "usuarios/registrar_rostro.html", {"usuario": usuario})


# =========================================================
# 🔹 ENDPOINTS AJAX (RECONOCIMIENTO FACIAL)
# =========================================================

@csrf_protect
@require_http_methods(["POST"])
def procesar_rostro(request):
    """
    Procesa y registra el rostro de un usuario.
    
    VALIDACIONES IMPLEMENTADAS:
    - Calidad del rostro
    - Detección de rostros duplicados
    - Activación automática del usuario
    """
    try:
        data = json.loads(request.body)
        usuario_id = data.get("usuario_id")
        image_data = data.get("image_data")

        if not usuario_id or not image_data:
            return JsonResponse({"success": False, "message": "Datos incompletos"}, status=400)

        usuario = get_object_or_404(Usuario, pk=usuario_id)

        # 1. VERIFICAR CALIDAD DEL ROSTRO
        quality_ok, quality_message = opencv_face_system.verify_face_quality(image_data)
        if not quality_ok:
            return JsonResponse({
                "success": False, 
                "message": f"❌ {quality_message or 'Calidad de imagen insuficiente'}"
            }, status=400)

        # 2. EXTRAER CARACTERÍSTICAS DEL ROSTRO (Encoding facial)
        encoding, message = opencv_face_system.encode_face_from_base64(image_data)
        if encoding is None:
            return JsonResponse({
                "success": False, 
                "message": f"❌ {message or 'No se detectó rostro válido'}"
            }, status=400)

        # 3. VERIFICAR QUE NO SEA UN ROSTRO DUPLICADO
        usuarios_con_rostro = Usuario.objects.filter(
            face_registered=True
        ).exclude(id=usuario_id)  # Excluir al usuario actual
        
        if usuarios_con_rostro.exists():
            # Cargar rostros conocidos para comparación
            opencv_face_system.load_known_faces(usuarios_con_rostro)
            
            if opencv_face_system.trained and len(opencv_face_system.known_faces) > 0:
                try:
                    # Intentar reconocer si este rostro ya existe
                    label, confidence = opencv_face_system.face_recognizer.predict(encoding)
                    
                    # Si la confianza es muy alta (< 50), es muy probable que sea el mismo rostro
                    if confidence < 50:
                        usuario_duplicado_id = opencv_face_system.known_ids.get(label)
                        try:
                            usuario_duplicado = Usuario.objects.get(id=usuario_duplicado_id)
                            return JsonResponse({
                                "success": False,
                                "message": f"⚠️ ROSTRO DUPLICADO: Este rostro ya está registrado para '{usuario_duplicado.nombre}' (ID: {usuario_duplicado.numero_identificacion}). Cada usuario debe tener un rostro único.",
                                "usuario_duplicado": {
                                    "nombre": usuario_duplicado.nombre,
                                    "id": usuario_duplicado.numero_identificacion
                                }
                            }, status=400)
                        except Usuario.DoesNotExist:
                            logger.warning(f"Usuario duplicado con ID {usuario_duplicado_id} no encontrado")
                except Exception as e:
                    logger.warning(f"Error verificando duplicados: {e}")

        # 4. GUARDAR IMAGEN FACIAL
        try:
            header, b64data = image_data.split(";base64,")
            ext = header.split("/")[-1]
            file_data = base64.b64decode(b64data)
            filename = f"user_{usuario.numero_identificacion}_{usuario.id}.{ext}"
            usuario.face_image.save(filename, ContentFile(file_data), save=False)
        except Exception as e:
            logger.exception(f"Error al guardar imagen facial: {e}")
            return JsonResponse({
                "success": False, 
                "message": "Error al guardar imagen"
            }, status=500)

        # 5. GUARDAR ENCODING
        enc_saved = opencv_face_system.save_face_encoding(encoding)
        if isinstance(enc_saved, np.ndarray):
            enc_saved = json.dumps(enc_saved.tolist())

        usuario.face_encoding = enc_saved
        usuario.face_registered = True
        usuario.activo = True  # ✅ ACTIVAR USUARIO AUTOMÁTICAMENTE
        usuario.save()

        messages.success(request, f"✅ Usuario {usuario.nombre} activado y rostro registrado exitosamente.")
        
        return JsonResponse({
            "success": True, 
            "message": f"✅ Rostro registrado exitosamente para {usuario.nombre}. Usuario activado."
        }, status=200)

    except Exception as e:
        logger.exception(f"Error en procesar_rostro: {e}")
        return JsonResponse({
            "success": False, 
            "message": f"Error interno del servidor: {str(e)}"
        }, status=500)


@csrf_protect
@require_http_methods(["POST"])
def reconocer_rostro(request):
    """
    Reconoce un rostro desde imagen base64 y valida permisos de acceso.
    
    VALIDACIONES IMPLEMENTADAS:
    - Usuario existe
    - Usuario está ACTIVO (no deshabilitado)
    - Usuario tiene permisos para el ambiente
    - Confianza mínima del 70%
    """
    try:
        data = json.loads(request.body)
        image_data = data.get("image_data")
        ambiente_id = data.get('ambiente')
        
        if not image_data:
            return JsonResponse({
                "success": False, 
                "message": "No se proporcionó imagen"
            }, status=400)
        
        if not ambiente_id:
            return JsonResponse({
                "success": False, 
                "message": "No se seleccionó un ambiente"
            }, status=400)

        try:
            ambiente = Ambiente.objects.get(pk=ambiente_id)
        except Ambiente.DoesNotExist:
            return JsonResponse({
                "success": False, 
                "message": "Ambiente no encontrado"
            }, status=404)

        # ✅ SOLO CARGAR USUARIOS ACTIVOS
        usuarios = Usuario.objects.filter(face_registered=True, activo=True)
        
        if not usuarios.exists():
            return JsonResponse({
                "success": False, 
                "message": "No hay usuarios activos registrados en el sistema"
            }, status=404)

        # Intentar reconocer el rostro
        user_id, confidence, message = opencv_face_system.recognize_face_from_base64(image_data, usuarios)

        if user_id:
            usuario = get_object_or_404(Usuario, pk=user_id)

            # ✅ VALIDACIÓN CRÍTICA: Verificar si el usuario está activo
            if not usuario.activo:
                # Registrar intento de acceso denegado
                Acceso.objects.create(
                    usuario=usuario,
                    ambiente=ambiente,
                    metodo='reconocimiento_facial',
                    acceso_permitido=False,
                    razon_denegacion='Usuario deshabilitado',
                    confianza=round((confidence or 0) * 100, 1)
                )
                
                return JsonResponse({
                    "success": False,
                    "acceso_autorizado": False,
                    "razon": "usuario_deshabilitado",
                    "message": f"❌ USUARIO DESHABILITADO - {usuario.nombre} no tiene acceso al sistema",
                    "usuario": {
                        "id": usuario.id,
                        "nombre": usuario.nombre,
                        "numero_identificacion": usuario.numero_identificacion,
                        "tipo": usuario.get_tipo_display(),
                    },
                    "confianza": round((confidence or 0) * 100, 1)
                }, status=200)

            # ✅ VERIFICACIÓN DE PERMISOS DE AMBIENTE - CRÍTICO
            if not usuario.tiene_permiso_ambiente(ambiente):
                # Registrar intento denegado
                Acceso.objects.create(
                    usuario=usuario,
                    ambiente=ambiente,
                    metodo='reconocimiento_facial',
                    acceso_permitido=False,
                    razon_denegacion=f'Usuario no tiene permiso para {ambiente.nombre}',
                    confianza=round((confidence or 0) * 100, 1)
                )
                
                return JsonResponse({
                    "success": False,
                    "message": f"🚫 NO TIENES PERMISO para acceder a {ambiente.nombre}",
                    "usuario": {
                        "id": usuario.id,
                        "nombre": usuario.nombre,
                        "numero_identificacion": usuario.numero_identificacion,
                        "tipo": usuario.get_tipo_display()
                    },
                    "ambiente": ambiente.nombre,
                    "confianza": round((confidence or 0) * 100, 1),
                    "acceso_autorizado": False,
                    "razon": "sin_permiso"
                }, status=200)

            # Migración automática de permisos si es necesario
            try:
                usuario.migrar_permisos_automaticamente()
            except Exception as e:
                logger.warning(f"Error en migración automática: {e}")

            # Alternar Entrada/Salida
            ultimo_registro = Registro.objects.filter(usuario=usuario).order_by("-fecha_hora").first()
            tipo_acceso = "Salida" if ultimo_registro and ultimo_registro.tipo == "Entrada" else "Entrada"

            # ✅ REGISTRAR ACCESO EXITOSO
            Registro.objects.create(
                usuario=usuario,
                tipo=tipo_acceso,
                metodo="facial",
                ambiente=ambiente.nombre,
                confianza=confidence or 0.0,
                fecha_hora=now()
            )

            Acceso.objects.create(
                usuario=usuario,
                ambiente=ambiente,
                metodo='reconocimiento_facial',
                acceso_permitido=True,
                razon_denegacion='',
                confianza=round((confidence or 0) * 100, 1)
            )

            return JsonResponse({
                "success": True,
                "message": f"✅ Bienvenido {usuario.nombre}",
                "usuario": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "numero_identificacion": usuario.numero_identificacion,
                    "tipo": usuario.get_tipo_display()
                },
                "ambiente": ambiente.nombre,
                "confianza": round((confidence or 0) * 100, 1),
                "acceso_autorizado": True,
                "tipo_acceso": tipo_acceso
            }, status=200)

        # Rostro no reconocido
        return JsonResponse({
            "success": False, 
            "message": message or "Rostro no reconocido con suficiente confianza", 
            "acceso_autorizado": False,
            "razon": "no_reconocido"
        }, status=200)

    except Exception as e:
        logger.exception(f"Error en reconocer_rostro: {e}")
        return JsonResponse({
            "success": False, 
            "message": "Error interno en el reconocimiento",
            "error": str(e)
        }, status=500)


@csrf_protect
@require_http_methods(["POST"])
def verificar_camara(request):
    return JsonResponse({"success": True, "message": "Cámara verificada correctamente"}, status=200)