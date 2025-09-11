from django.urls import path
from .views import listar_ambientes, crear_ambiente, editar_ambiente

urlpatterns = [
    path('', listar_ambientes, name='listar_ambientes'),
    path('crear/', crear_ambiente, name='crear_ambiente'),
    path('editar/<int:pk>/', editar_ambiente, name='editar_ambiente'),
]
