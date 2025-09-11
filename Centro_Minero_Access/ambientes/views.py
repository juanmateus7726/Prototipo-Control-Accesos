from django.shortcuts import render, get_object_or_404, redirect
from .models import Ambiente
from .forms import AmbienteForm

def listar_ambientes(request):
    ambientes = Ambiente.objects.all()
    return render(request, 'ambientes/listar_ambientes.html', {'ambientes': ambientes})

def crear_ambiente(request):
    if request.method == 'POST':
        form = AmbienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_ambientes')
    else:
        form = AmbienteForm()
    return render(request, 'ambientes/crear_ambiente.html', {'form': form})

def editar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    if request.method == 'POST':
        form = AmbienteForm(request.POST, instance=ambiente)
        if form.is_valid():
            form.save()
            return redirect('listar_ambientes')
    else:
        form = AmbienteForm(instance=ambiente)
    return render(request, 'ambientes/editar_ambiente.html', {'form': form})

def eliminar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    if request.method == 'POST':
        ambiente.delete()
        return redirect('listar_ambientes')
    return render(request, 'ambientes/eliminar_ambiente.html', {'ambiente': ambiente})
