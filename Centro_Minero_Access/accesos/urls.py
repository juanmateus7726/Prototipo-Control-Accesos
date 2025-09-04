from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('historial/', views.historial_accesos, name='accesos_historial'),
    path('detector/', views.detector_view, name='accesos_detector'),
]