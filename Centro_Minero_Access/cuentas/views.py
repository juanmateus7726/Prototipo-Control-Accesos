# views.py - ACTUALIZADO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_protect


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    """
    Vista principal después de iniciar sesión.
    Muestra los grupos del usuario logueado.
    """
    context = {
        'user_groups': request.user.groups.all(),
    }
    return render(request, 'cuentas/dashboard.html', context)


# =========================
# REGISTRO (solo superusuarios)
# =========================
@user_passes_test(lambda u: u.is_superuser)
def register(request):
    """
    Solo el superusuario puede registrar nuevos usuarios.
    Por defecto, los usuarios nuevos se asignan al grupo 'Instructores'.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Usa el formulario personalizado
        if form.is_valid():
            # Crear usuario sin guardar aún para asignarle el grupo
            user = form.save(commit=False)
            user.save()

            # Asignar al grupo "Instructores" automáticamente
            group, created = Group.objects.get_or_create(name='Instructores')
            user.groups.add(group)

            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f'✅ ¡Usuario "{username}" creado exitosamente! '
                f'Asignado al grupo "{group.name}".'
            )
            return redirect('cuentas:dashboard')
        else:
            messages.error(
                request,
                '❌ Error en el formulario. Por favor revisa los campos.'
            )
    else:
        form = CustomUserCreationForm()

    return render(request, 'cuentas/register.html', {'form': form})


# =========================
# LOGOUT PERSONALIZADO
# =========================
@csrf_protect
@login_required
def custom_logout(request):
    """
    Muestra una página de confirmación de cierre de sesión
    y cierra sesión cuando el usuario confirma (POST).
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
        return redirect('accesos:control_acceso')  # Ajusta a tu vista de inicio

    return render(request, 'cuentas/logout.html')
