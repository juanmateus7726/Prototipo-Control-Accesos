from django.urls import path
from . import views

app_name = 'laboratorios'

urlpatterns = [
    # Página principal (index)
    path('', views.index, name='index'),
    # Selección de laboratorio
    path('seleccionar/', views.seleccionar_laboratorio, name='seleccionar'),
    # Sala de laboratorio (recibe lab_id)
    path('sala/<int:lab_id>/', views.sala_laboratorio, name='sala'),
    # Historial de accesos
    path('historial/', views.historial_accesos, name='historial'),
    # Acceso general
    path('acceso/', views.acceso, name='acceso'),
    path('logout/', views.cerrar_sesion, name='logout'),
]
