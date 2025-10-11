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
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accesibilidad/', views.accesibilidad, name='accesibilidad'),

    # === Recuperación de Contraseña ===
    
    # Paso 1: Solicitar correo electrónico
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='cuentas/password_reset.html',
            email_template_name='cuentas/password_reset_email.txt',
            subject_template_name='cuentas/password_reset_subject.txt',
            success_url='/cuentas/password-reset/done/',
            from_email='tatisalexa16@gmail.com'
        ),
        name='password_reset'
    ),

    # Paso 2: Confirmación de correo enviado
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='cuentas/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # Paso 3: Formulario para nueva contraseña (desde el enlace del correo)
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='cuentas/password_reset_confirm.html',
            success_url='/cuentas/reset/complete/'
        ),
        name='password_reset_confirm'
    ),

    # Paso 4: Confirmación final - contraseña cambiada
    path(
        'reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='cuentas/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]