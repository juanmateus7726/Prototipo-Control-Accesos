from django.urls import path
from . import views

app_name = 'ambientes'

urlpatterns = [
    path('', views.listar_ambientes, name='listar_ambientes'),
    path('crear/', views.crear_ambiente, name='crear_ambiente'),
    path('editar/<int:pk>/', views.editar_ambiente, name='editar_ambiente'),
    path('eliminar/<int:pk>/', views.eliminar_ambiente, name='eliminar_ambiente'),
]
