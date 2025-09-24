from django.urls import path 
from .views import control_acceso_view, listar_accesos
from . import views

app_name = 'accesos'

urlpatterns = [
    # Asegúrate de que esta línea exista y tenga name='control_acceso'
    path('', control_acceso_view, name='control_acceso'),
    
    path("lista/", listar_accesos, name="lista"),
    path('ambiente/<int:ambiente_id>/', views.ambiente_detalle, name='ambiente_detalle'),

]