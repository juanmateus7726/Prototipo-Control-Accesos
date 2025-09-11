from django.shortcuts import render, redirect
from .models import Acceso, Usuario
from .forms import AccesoForm

def home(request):
    return redirect('accesos') # Redirige a la vista de accesos

def accesos_view(request):
    if request.method == "POST":
        form = AccesoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accesos")  # Redirige a la misma página
    else:
        form = AccesoForm()

    # Para la tabla/listado de accesos
    accesos_lista = Acceso.objects.all().order_by("-fecha_hora")

    context = {
        "form": form,
        "accesos_lista": accesos_lista
    }
    return render(request, "accesos/index.html", context)