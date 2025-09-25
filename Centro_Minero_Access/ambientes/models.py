from django.db import models
from django.utils import timezone

class Ambiente(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True, default='000')
    estado = models.CharField(max_length=20, choices=[
        ('Disponible', 'Disponible'),
        ('Ocupado', 'Ocupado'),
        ('Mantenimiento', 'Mantenimiento'),
    ], default='Disponible')
    capacidad = models.IntegerField(default=1)
    riesgo = models.CharField(max_length=20, choices=[
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('muy_alto', 'Muy Alto'),
    ], default='bajo')
    
    def __str__(self):
        return self.nombre
    def resumen_protocolos(self):
        """
        Retorna un resumen de protocolos para este ambiente.
        Ej: {'total': 5, 'completados': 2, 'pendientes': 3, 'tareas_pendientes': ['Tarea1', 'Tarea2']}
        """
        from .models import ProtocoloAmbiente, TareaProtocolo  # Importa aquí para evitar circular imports
        protocolos = ProtocoloAmbiente.objects.filter(ambiente=self)
        total = protocolos.count()
        completados = protocolos.filter(completado=True).count()
        pendientes = total - completados
        
        # Lista de descripciones de tareas pendientes (solo las primeras 3 para no sobrecargar)
        tareas_pendientes = [
            p.tarea.descripcion for p in protocolos.filter(completado=False)[:3]
        ]
        
        return {
            'total': total,
            'completados': completados,
            'pendientes': pendientes,
            'tareas_pendientes': tareas_pendientes
        }

# Nuevo modelo para las tareas de protocolo
class TareaProtocolo(models.Model):
    descripcion = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.descripcion
    
# Nuevo modelo para el checklist de cada ambiente
class ProtocoloAmbiente(models.Model):
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='protocolos')
    tarea = models.ForeignKey(TareaProtocolo, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('ambiente', 'tarea')
    
    def __str__(self):
        return f'Protocolo para {self.ambiente.nombre}: {self.tarea.descripcion}'