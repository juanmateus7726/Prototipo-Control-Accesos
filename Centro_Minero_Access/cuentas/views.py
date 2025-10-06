# views.py - ACTUALIZADO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm 
from django.views.decorators.csrf import csrf_protect

@login_required
def dashboard(request):
    context = {
        'user_groups': request.user.groups.all(),
    }
    return render(request, 'cuentas/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Usa tu formulario personalizado
        if form.is_valid():
            user = form.save(commit=False)
            group, created = Group.objects.get_or_create(name='Instructores')
            user.groups.add(group)
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Usuario {username} creado exitosamente! Asignado a grupo "{group.name}".')
            return redirect('cuentas:dashboard')
        else:
            messages.error(request, 'Error en el formulario. Revisa los campos.')
    else:
        form = CustomUserCreationForm()  # Usa tu formulario personalizado
    return render(request, 'cuentas/register.html', {'form': form})

@csrf_protect
@login_required
def custom_logout(request):
    if request.method == 'POST':
        # Si es POST, cerrar sesión y redirigir
        logout(request)
        return redirect('accesos:control_acceso')  # Ajusta según tu app principal
    
    # Si es GET, mostrar tu template personalizado
    return render(request, 'cuentas/logout.html')