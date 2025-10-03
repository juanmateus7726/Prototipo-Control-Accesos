from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages
from .models import Ambiente, TareaProtocolo, ProtocoloAmbiente
from .forms import AmbienteForm


# 🔹 Vista para listar ambientes ACTIVOS
def listar_ambientes(request):
    ambientes = Ambiente.objects.filter(activo=True).order_by('nombre')
    return render(request, 'ambientes/listar_ambientes.html', {'ambientes': ambientes})


# 🔹 Vista para listar ambientes DESHABILITADOS (opcional)
def listar_ambientes_deshabilitados(request):
    ambientes = Ambiente.objects.filter(activo=False).order_by('nombre')
    return render(request, 'ambientes/listar_ambientes_deshabilitados.html', {'ambientes': ambientes})


# 🔹 Crear un nuevo ambiente
def crear_ambiente(request):
    if request.method == 'POST':
        form = AmbienteForm(request.POST)
        if form.is_valid():
            try:
                nuevo_ambiente = form.save()

                # Crear automáticamente protocolos para el nuevo ambiente
                tareas_protocolo = TareaProtocolo.objects.all()
                for tarea in tareas_protocolo:
                    ProtocoloAmbiente.objects.create(
                        ambiente=nuevo_ambiente,
                        tarea=tarea,
                        completado=False,
                    )

                messages.success(request, "✅ Ambiente creado exitosamente y protocolo generado.")
                return redirect('ambientes:listar_ambientes')

            except IntegrityError:
                messages.error(request, "⚠️ Ya existe un ambiente con este código. Intente con otro.")
    else:
        form = AmbienteForm()

    return render(request, 'ambientes/crear_ambiente.html', {'form': form})


# 🔹 Editar un ambiente existente
def editar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    protocolos = ambiente.protocolos.all().order_by('tarea__descripcion')

    if request.method == 'POST':
        form = AmbienteForm(request.POST, instance=ambiente)
        if form.is_valid():
            form.save()

            # Actualizar el checklist
            for protocolo in protocolos:
                is_checked = request.POST.get(f'protocolo_{protocolo.id}') == 'on'
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

            messages.success(request, "✅ Ambiente y protocolo actualizados correctamente.")
            return redirect('ambientes:listar_ambientes')
    else:
        form = AmbienteForm(instance=ambiente)

    return render(request, 'ambientes/editar_ambiente.html', {
        'form': form,
        'ambiente': ambiente,
        'protocolos': protocolos,
    })


# 🔹 Nueva vista para DESHABILITAR un ambiente (Soft Delete)
def deshabilitar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    if request.method == 'POST':
        ambiente.activo = False
        ambiente.save()
        messages.success(request, f"🚫 El ambiente '{ambiente.nombre}' fue deshabilitado.")
        return redirect('ambientes:listar_ambientes')

    return render(request, 'ambientes/deshabilitar_ambiente.html', {'ambiente': ambiente})


# 🔹 Nueva vista para REACTIVAR un ambiente
def reactivar_ambiente(request, pk):
    ambiente = get_object_or_404(Ambiente, pk=pk)
    if request.method == 'POST':
        ambiente.activo = True
        ambiente.save()
        messages.success(request, f"✅ El ambiente '{ambiente.nombre}' fue reactivado.")
        return redirect('ambientes:listar_ambientes_deshabilitados')

    return render(request, 'ambientes/reactivar_ambiente.html', {'ambiente': ambiente})
