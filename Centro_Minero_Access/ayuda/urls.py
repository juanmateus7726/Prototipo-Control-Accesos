from django.urls import path
from . import views

app_name = 'ayuda'

urlpatterns = [
    path('', views.pagina_ayuda, name='index'),
    path('manual/', views.descargar_manual, name='manual_usuario'),
]