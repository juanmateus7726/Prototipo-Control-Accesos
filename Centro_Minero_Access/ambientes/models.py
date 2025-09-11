from django.db import models

class Ambiente(models.Model):
    nombre = models.CharField(max_length=100)
    protocolo = models.TextField()
    riesgo = models.CharField(max_length=20, choices=[
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('muy_alto', 'Muy Alto'),
    ])
    
    def __str__(self):
        return self.nombre