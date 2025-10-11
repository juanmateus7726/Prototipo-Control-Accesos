from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.backup_list, name='backup_list'),
    path('crear/', views.crear_backup, name='crear_backup'),
    path('descargar/<str:filename>/', views.descargar_backup, name='descargar_backup'),
    path('eliminar/<str:filename>/', views.eliminar_backup, name='eliminar_backup'),
]