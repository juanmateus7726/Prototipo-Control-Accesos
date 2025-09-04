from django.urls import path
from . import views

app_name = 'laboratorio'

urlpatterns = [
    path('acceso/', views.acceso, name='acceso'),
    path('historial/', views.historial, name='historial'),
    path('sala/', views.sala, name='sala'),
]
