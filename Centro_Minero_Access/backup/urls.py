from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    # Listar todos los backups
    path('', views.backup_list, name='backup_list'),
    
    # Crear nuevo backup
    path('crear/', views.crear_backup, name='crear_backup'),
    
    # Descargar backup
    path('descargar/<str:filename>/', views.descargar_backup, name='descargar_backup'),
    
    # Eliminar backup
    path('eliminar/<str:filename>/', views.eliminar_backup, name='eliminar_backup'),
    
    # Restaurar backup
    path('restaurar/<str:filename>/', views.restaurar_backup, name='restaurar_backup'),
]