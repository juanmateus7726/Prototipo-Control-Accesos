from django.db import models

# Create your models here.
class Usuario(models.Model):
     TIPO_USUARIO = [
         ('instructor', 'Instructor'),
         ('aprendiz', 'Aprendiz'),
         ('administartivo', 'Administrativo'),
         ('visitante', 'Visitante'),
         ('restringido', 'Registro'),
     ]
     
     carnet = models.CharField(max_length=8, unique=True)
     nombre = models.CharField (max_length=100)
     tipo = models.CharField(max_length=20, choices=TIPO_USUARIO)
     activo = models.BooleanField(default=True)
     
     def __str__(self):
         return self.nombre