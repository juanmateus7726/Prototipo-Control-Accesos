from django.urls import path
from . import views

app_name = 'usuarios'


urlpatterns = [
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Nueva URL para la lista de registros
    path('registros/', views.listar_registros, name='listar_registros'),
]