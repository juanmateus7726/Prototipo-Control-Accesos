from django.db import models
from usuarios.models import Usuario
from ambientes.models import Ambiente  # ¡Importa el modelo Ambiente!

class Acceso(models.Model):
    # Opciones para el método de acceso
    METODO_CHOICES = [
        ('manual', 'Acceso Manual'),
        ('reconocimiento_facial', 'Reconocimiento Facial'),
        ('huella_dactilar', 'Huella Dactilar'), # Futuro
        ('tarjeta_rfid', 'Tarjeta RFID'), # Futuro
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # Cambia de CharField a un ForeignKey que se enlaza al modelo Ambiente
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    metodo = models.CharField(max_length=30, choices=METODO_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    acceso_permitido = models.BooleanField(default=False)
    razon_denegacion = models.CharField(max_length=200, blank=True)
    confianza = models.FloatField(null=True, blank=True, default=None)
    
    def __str__(self):
        # Ahora puedes acceder al nombre del ambiente a través de la relación
        return f"{self.usuario} - {self.ambiente.nombre} - {self.fecha_hora}"
    
    class Meta:
        verbose_name = "Acceso"
        verbose_name_plural = "Accesos"
        ordering = ['-fecha_hora']