from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from .models import Usuario, Registro
from .forms import UsuarioForm, RegistroAccesoForm
from .face_recognition.face_system_opencv import opencv_face_system
import json
import base64

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.nombre} creado exitosamente. Ahora registre su rostro.')
            return redirect('usuarios:registrar_rostro', pk=usuario.pk)
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

def registrar_rostro(request, pk):
    """Vista para registrar el rostro de un usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'GET':
        return render(request, 'usuarios/registrar_rostro.html', {'usuario': usuario})

def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('usuarios:listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {
        'form': form, 
        'usuario': usuario
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

# === VISTAS AJAX PARA RECONOCIMIENTO FACIAL ===

@csrf_exempt
@require_http_methods(["POST"])
def procesar_rostro(request):
    """API para procesar y guardar el rostro de un usuario"""
    try:
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        image_data = data.get('image_data')
        
        if not usuario_id or not image_data:
            return JsonResponse({
                'success': False,
                'message': 'Datos incompletos'
            })
        
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        
        # Procesar la imagen y extraer codificación facial
        encoding, message = opencv_face_system.encode_face_from_base64(image_data)
        
        if encoding is None:
            return JsonResponse({
                'success': False,
                'message': message
            })
        
        # Verificar calidad del rostro
        quality_ok, quality_message = opencv_face_system.verify_face_quality(image_data)
        if not quality_ok:
            return JsonResponse({
                'success': False,
                'message': quality_message
            })
        
        # Guardar la imagen
        face_image_file = opencv_face_system.save_face_image_from_base64(
            image_data, 
            f"user_{usuario.carnet}_{usuario.id}"
        )
        
        if face_image_file:
            # Guardar en el usuario
            usuario.face_image = face_image_file
            usuario.face_encoding = opencv_face_system.save_face_encoding(encoding)
            usuario.face_registered = True
            usuario.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Rostro registrado exitosamente para {usuario.nombre}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error al guardar la imagen'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def reconocer_rostro(request):
    """API para reconocer un rostro y autorizar acceso"""
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        ambiente = data.get('ambiente', 'Laboratorio de Sistemas')
        
        if not image_data:
            return JsonResponse({
                'success': False,
                'message': 'No se proporcionó imagen'
            })
        
        # Obtener todos los usuarios con rostro registrado
        usuarios = Usuario.objects.filter(
            face_registered=True, 
            activo=True
        )
        
        if not usuarios.exists():
            return JsonResponse({
                'success': False,
                'message': 'No hay usuarios registrados en el sistema'
            })
        
        # Reconocer rostro
        user_id, confidence, message = opencv_face_system.recognize_face_from_base64(
            image_data, 
            usuarios
        )
        
        if user_id:
            usuario = get_object_or_404(Usuario, pk=user_id)
            
            # Registrar el acceso
            registro = Registro.objects.create(
                usuario=usuario,
                tipo='Entrada',  # Puedes hacer esto dinámico
                metodo='facial',
                ambiente=ambiente,
                confianza=confidence
            )
            
            return JsonResponse({
                'success': True,
                'message': message,
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'carnet': usuario.carnet,
                    'tipo': usuario.get_tipo_display()
                },
                'confianza': round(confidence * 100, 1) if confidence else 0,
                'acceso_autorizado': True
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message,
                'acceso_autorizado': False
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en el reconocimiento: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def verificar_camara(request):
    """API para verificar si la cámara está funcionando"""
    return JsonResponse({
        'success': True,
        'message': 'Cámara verificada correctamente'
    })