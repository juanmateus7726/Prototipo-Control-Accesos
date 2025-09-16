from django.shortcuts import render, redirect
from accesos.models import Acceso   # 👈 Solo Acceso si Usuario está en otra app
from usuarios.models import Usuario  # 👈 Importa el modelo real de usuarios
from .forms import AccesoForm


def index(request):
    """
    Vista principal del panel de accesos.
    Muestra los últimos accesos, el formulario y los usuarios registrados.
    """
    accesos_lista = Acceso.objects.all().order_by("-fecha_hora")[:10]
    usuarios = Usuario.objects.all()
    form = AccesoForm()

    context = {
        "accesos_lista": accesos_lista,
        "usuarios": usuarios,
        "form": form,
    }
    return render(request, "accesos/index.html", context)


def registrar_acceso(request):
    """
    Vista para registrar un nuevo acceso manual.
    También devuelve la lista de accesos y usuarios para mostrar en la misma página.
    """
    if request.method == "POST":
        form = AccesoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accesos:index")  # Ajusta el nombre según tus urls
    else:
        form = AccesoForm()

    accesos_lista = Acceso.objects.all().order_by("-fecha_hora")
    usuarios = Usuario.objects.all()

    context = {
        "form": form,
        "accesos_lista": accesos_lista,
        "usuarios": usuarios,
    }
    return render(request, "accesos/index.html", context)
