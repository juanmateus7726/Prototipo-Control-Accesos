from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # URLs principales
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('registros/', views.listar_registros, name='listar_registros'),
    
    # URLs para reconocimiento facial
    path('registrar-rostro/<int:pk>/', views.registrar_rostro, name='registrar_rostro'),
    
    # APIs AJAX
    path('api/procesar-rostro/', views.procesar_rostro, name='procesar_rostro'),
    path('api/reconocer-rostro/', views.reconocer_rostro, name='reconocer_rostro'),
    path('api/verificar-camara/', views.verificar_camara, name='verificar_camara'),
]