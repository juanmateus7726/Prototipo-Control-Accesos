from django.urls import path 
from . import views

app_name = 'accesos'

urlpatterns = [
    path('', views.index, name='index'),
    path("lista/", views.listar_accesos, name="lista"),

]