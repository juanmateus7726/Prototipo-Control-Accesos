from django.urls import path
from . import views

urlpatterns = [
    path('reporte-accesos/', views.reporte_accesos_pdf, name='reporte_accesos_pdf'),
]
