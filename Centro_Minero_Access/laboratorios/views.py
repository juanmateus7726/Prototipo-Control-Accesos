from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Laboratorio, AccesoLaboratorio
from django.contrib.auth import logout
from django.shortcuts import redirect


# ==============================
# Página de inicio / index
# ==============================
@login_required
def index(request):
    return render(request, 'laboratorios/index.html')


# ==============================
# Selección de laboratorio
# ==============================
@login_required
def seleccionar_laboratorio(request):
    laboratorios = Laboratorio.objects.all()

    if request.method == 'POST':
        lab_id = request.POST.get('laboratorios')
        lab = get_object_or_404(Laboratorio, id=lab_id)
        usuario = request.user
        autorizado = lab in usuario.laboratorios_permitidos.all()

        # Registrar acceso
        AccesoLaboratorio.objects.create(
            usuario=usuario,
            laboratorio=lab,
            autorizado=autorizado,
            motivo_denegado=None if autorizado else "No tiene permisos"
        )

        return redirect('laboratorio:sala', lab_id=lab.id)

    return render(request, 'laboratorios/seleccion.html', {'laboratorios': laboratorios})


# ==============================
# Sala del laboratorio
# ==============================
@login_required
def sala_laboratorio(request, lab_id):
    lab = get_object_or_404(Laboratorio, id=lab_id)
    usuario = request.user
    autorizado = lab in usuario.laboratorios_permitidos.all()

    return render(request, 'laboratorios/sala.html', {
        'laboratorio': lab,
        'autorizado': autorizado
    })


# ==============================
# Historial de accesos
# ==============================
@login_required
def historial_accesos(request):
    registros = AccesoLaboratorio.objects.filter(usuario=request.user).order_by('-fecha_hora')
    return render(request, 'laboratorios/historial.html', {'registros': registros})


# ==============================
# Página de acceso (acceso.html)
# ==============================
@login_required
def acceso(request):
    return render(request, 'laboratorios/acceso.html')




def cerrar_sesion(request):
    logout(request)
    return redirect('login')  # o a la página que quieras
