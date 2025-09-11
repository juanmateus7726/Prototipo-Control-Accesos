from django.urls import path
from .views import listar_usuarios, crear_usuario, editar_usuario, eliminar_usuario

urlpatterns = [
    path('', listar_usuarios, name='listar_usuario'),
    path('crear/', crear_usuario, name='crear_usuario'),
    path('editar/<int:pk>/', editar_usuario, name='editar_usuario'),
    path('eliminar/<int:pk>', eliminar_usuario, name='eliminar_usuario'),
]