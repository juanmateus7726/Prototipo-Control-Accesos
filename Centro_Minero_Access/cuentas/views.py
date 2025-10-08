from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from django.utils.timezone import now

from accesos.models import Acceso
from usuarios.models import Usuario
from ambientes.models import Ambiente


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    """
    Vista principal del panel de control.
    """
    # Totales
    total_usuarios = Usuario.objects.count()

    # Contar solo ambientes activos
    total_ambientes = Ambiente.objects.filter(activo=True).count()

    # Accesos de hoy (usamos __date porque fecha_hora es DateTimeField)
    hoy = now().date()
    accesos_hoy = Acceso.objects.filter(fecha_hora__date=hoy).count()

    context = {
        'total_usuarios': total_usuarios,
        'total_ambientes': total_ambientes,
        'accesos_hoy': accesos_hoy,
        'user_groups': request.user.groups.all()
    }

    return render(request, 'cuentas/dashboard.html', context)


# =========================
# REGISTRO (solo superusuarios)
# =========================
@user_passes_test(lambda u: u.is_superuser)
def register(request):
    from .forms import CustomUserCreationForm

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Asignar grupo por defecto al usuario nuevo
            group, created = Group.objects.get_or_create(name='Instructores')
            user.groups.add(group)

            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f'✅ ¡Usuario "{username}" creado exitosamente y asignado al grupo "{group.name}"!'
            )
            return redirect('cuentas:dashboard')
        else:
            messages.error(request, '❌ Error en el formulario. Revisa los campos.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'cuentas/register.html', {'form': form})


# =========================
# LOGOUT
# =========================
@csrf_protect
@login_required
def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
        return redirect('accesos:control_acceso')

    return render(request, 'cuentas/logout.html')
