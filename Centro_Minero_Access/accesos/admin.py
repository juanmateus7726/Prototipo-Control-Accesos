from django.contrib import admin
from .models import Acceso

@admin.register(Acceso)
class AccesoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ambiente', 'metodo', 'fecha_hora', 'acceso_permitido')
    list_filter = ('ambiente', 'metodo', 'acceso_permitido')
    search_fields = ('usuario__nombre', 'usuario__numero_identificacion')
    ordering = ('-fecha_hora',)
