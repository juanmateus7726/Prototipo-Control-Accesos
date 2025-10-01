from django.urls import path
from . import views

app_name = 'ambientes'

urlpatterns = [
    # Listado de ambientes activos
    path('', views.listar_ambientes, name='listar_ambientes'),

    # Listado de ambientes deshabilitados
    path('deshabilitados/', views.listar_ambientes_deshabilitados, name='listar_ambientes_deshabilitados'),

    # Crear y editar ambientes
    path('crear/', views.crear_ambiente, name='crear_ambiente'),
    path('editar/<int:pk>/', views.editar_ambiente, name='editar_ambiente'),

    # Nueva ruta para deshabilitar (soft delete)
    path('deshabilitar/<int:pk>/', views.deshabilitar_ambiente, name='deshabilitar_ambiente'),

    # Nueva ruta para reactivar ambientes
    path('reactivar/<int:pk>/', views.reactivar_ambiente, name='reactivar_ambiente'),
]
