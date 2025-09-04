from django.shortcuts import render, redirect
from .models import Acceso

# Create your views here.

def index(request):
    return render(request, 'accesos/index.html')

def registrar_acceso(request):
    if request.method == "POST":
        usuario = request.POST['usuario']
        tipo = request.POST['tipo']
        laboratorio = request.POST['laboratorio']
        Acceso.objects.create(usuario=usuario, tipo=tipo, laboratorio=laboratorio)
        return redirect('historial_accesos')
    return render(request, 'accesos/registrar.html')

def historial_accesos(request):
    # Obtener todos los accesos registrados
    accesos = Acceso.objects.all().order_by('-fecha_hora') 
    return render(request, 'accesos/historial.html', {'accesos': accesos})

def detector_view(request):
    return render(request, 'accesos/detector.html')