from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    # === Autenticación ===
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='cuentas/login.html',
            redirect_authenticated_user=True  # Redirige si ya está logueado
        ),
        name='login'
    ),
    
    path('logout/', views.custom_logout, name='logout'),

    # === Registro de usuarios ===
    path('register/', views.register, name='register'),

    # === Dashboard protegido ===
    path('dashboard/', views.dashboard, name='dashboard'),
]
