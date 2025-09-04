from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Laboratorio, AccesoLaboratorio

# ==============================
# Vista para seleccionar laboratorio
# ==============================
@login_required
def seleccionar_laboratorio(request):
    laboratorios = Laboratorio.objects.all()
    
    if request.method == 'POST':
        lab_id = request.POST.get('laboratorio')
        if not lab_id:
            # Manejo de error si no se selecciona ningún laboratorio
            return render(request, 'laboratorio/seleccion.html', {
                'laboratorios': laboratorios,
                'error': "Debes seleccionar un laboratorio."
            })

        lab = get_object_or_404(Laboratorio, id=lab_id)
        usuario = request.user
        autorizado = lab in usuario.laboratorios_permitidos.all()

        # Crear registro de acceso
        AccesoLaboratorio.objects.create(
            usuario=usuario,
            laboratorio=lab,
            autorizado=autorizado,
            motivo_denegado=None if autorizado else "No tiene permisos"
        )

        # Redirigir a la sala del laboratorio
        return redirect('sala_laboratorio', lab_id=lab.id)
    
    return render(request, 'laboratorio/seleccion.html', {'laboratorios': laboratorios})


# ==============================
# Vista para la sala de laboratorio
# ==============================
@login_required
def sala_laboratorio(request, lab_id):
    lab = get_object_or_404(Laboratorio, id=lab_id)
    usuario = request.user
    autorizado = lab in usuario.laboratorios_permitidos.all()

    context = {
        'laboratorio': lab,
        'autorizado': autorizado
    }

    # Opcional: registrar acceso automático si se desea
    # AccesoLaboratorio.objects.create(
    #     usuario=usuario,
    #     laboratorio=lab,
    #     autorizado=autorizado,
    #     motivo_denegado=None if autorizado else "No tiene permisos"
    # )

    return render(request, 'laboratorio/sala.html', context)


# ==============================
# Vista para historial de accesos
# ==============================
@login_required
def historial_accesos(request):
    registros = AccesoLaboratorio.objects.filter(usuario=request.user).order_by('-fecha_hora')
    return render(request, 'laboratorio/historial.html', {'registros': registros})
