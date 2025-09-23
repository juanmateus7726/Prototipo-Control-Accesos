from django.contrib import admin
from .models import Ambiente, TareaProtocolo, ProtocoloAmbiente

# Registro del modelo Ambiente
@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'estado', 'capacidad', 'riesgo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('estado', 'riesgo')

# Registro del modelo TareaProtocolo
@admin.register(TareaProtocolo)
class TareaProtocoloAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    search_fields = ('descripcion',)
    
# Registro del modelo ProtocoloAmbiente
@admin.register(ProtocoloAmbiente)
class ProtocoloAmbienteAdmin(admin.ModelAdmin):
    list_display = ('ambiente', 'tarea', 'completado', 'fecha_completado')
    list_filter = ('ambiente', 'completado')
    search_fields = ('ambiente__nombre', 'tarea__descripcion')