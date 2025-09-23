from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.utils import timezone
from .models import Ambiente, TareaProtocolo, ProtocoloAmbiente
from .forms import AmbienteForm
from django.contrib import messages

# Vista para listar todos los ambientes
def listar_ambientes(request):
    ambientes = Ambiente.objects.all().order_by('nombre')
    return render(request, 'ambientes/listar_ambientes.html', {'ambientes': ambientes})

# Vista para crear un nuevo ambiente
def crear_ambiente(request):
    if request.method == 'POST':
        form = AmbienteForm(request.POST)
        if form.is_valid():
            try:
                nuevo_ambiente = form.save()
                
                # Obtener todas las tareas de protocolo predefinidas
                # y crear un ProtocoloAmbiente por cada una
                tareas_protocolo = TareaProtocolo.objects.all()
                for tarea in tareas_protocolo:
                    ProtocoloAmbiente.objects.create(
                        ambiente=nuevo_ambiente,
                        tarea=tarea,
                        completado=False,
                    )
                
                messages.success(request, "Ambiente creado exitosamente y protocolo de seguridad generado.")
                return redirect('ambientes:listar_ambientes')
            except IntegrityError:
                # Capturar el error si el código del ambiente ya existe
                messages.error(request, "Ya existe un ambiente con este código. Por favor, ingrese uno diferente.")
    else:
        form = AmbienteForm()
    
    return render(request, 'ambientes/crear_ambiente.html', {'form': form})

# Vista para editar un ambiente existente
def editar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    protocolos = ambiente.protocolos.all().order_by('tarea__descripcion')

    if request.method == 'POST':
        form = AmbienteForm(request.POST, instance=ambiente)
        if form.is_valid():
            form.save()
            
            # Procesar el checklist del formulario
            for protocolo in protocolos:
                is_checked = request.POST.get(f'protocolo_{protocolo.id}') == 'on'
                
                # Usamos una variable para saber si hubo cambios
                cambio_estado = False

                if is_checked and not protocolo.completado:
                    protocolo.completado = True
                    protocolo.fecha_completado = timezone.now()
                    cambio_estado = True
                elif not is_checked and protocolo.completado:
                    protocolo.completado = False
                    protocolo.fecha_completado = None
                    cambio_estado = True
                
                if cambio_estado:
                    protocolo.save()

            messages.success(request, "Ambiente y protocolo actualizados exitosamente.")
            return redirect('ambientes:listar_ambientes')
    else:
        form = AmbienteForm(instance=ambiente)

    return render(request, 'ambientes/editar_ambiente.html', {
        'form': form,
        'ambiente': ambiente,
        'protocolos': protocolos,
    })

# Vista para eliminar un ambiente
def eliminar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    if request.method == 'POST':
        ambiente.delete()
        messages.success(request, "El ambiente fue eliminado correctamente.")
        return redirect('ambientes:listar_ambientes')
    
    return render(request, 'ambientes/eliminar_ambiente.html', {'ambiente': ambiente})