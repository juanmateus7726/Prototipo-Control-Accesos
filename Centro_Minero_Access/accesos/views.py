from django.shortcuts import render, redirect
from .models import Acceso, Usuario
from .forms import AccesoForm


def index(request):
    accesos_lista = Acceso.objects.all().order_by("-fecha_hora")[:10]
    form = AccesoForm()
    return render(request, 'index.html', {'accesos_lista': accesos_lista, 'form': form})

def accesos(request):
    if request.method == "POST":
        form = AccesoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accesos")  # redirige a la misma página
    else:
        form = AccesoForm()

    # Para la tabla / listado de accesos
    accesos_lista = Acceso.objects.all().order_by("-fecha_hora")

    context = {
        "form": form,
        "accesos_lista": accesos_lista
    }
    return render(request, "accesos/index.html", context)