from django.urls import path
from .views import accesos_view

urlpatterns = [
    path('', accesos_view, name='accesos'),
    
]