from django.db import models

# Create your models here.
class Acceso(models.Model):
    usuario = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=[("entrada", "Entrada"), ("salida", "Salida")])
    laboratorio = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.tipo} ({self.fecha_hora})"