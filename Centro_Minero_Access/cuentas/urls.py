from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    # Login (usa template custom con campos manuales)
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html',
        redirect_authenticated_user=True,  # Si ya logueado, redirige a dashboard
    ), name='login'),
    
    # Logout (redirige a index de accesos)
    path('logout/', views.custom_logout, name='logout'),
    
    # Register restringido
    path('register/', views.register, name='register'),
    
    # Dashboard (protegido)
    path('dashboard/', views.dashboard, name='dashboard'),
]
