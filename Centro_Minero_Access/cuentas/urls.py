from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    # ===========================
    # 🔹 Login / Logout
    # ===========================
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html'   # ✅ RUTA CORRECTA
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'                        # redirige al cerrar sesión
    ), name='logout'),

    # 🔹 Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
