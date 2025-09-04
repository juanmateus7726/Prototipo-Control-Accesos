from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    # Aqui se puede agregar campos extra como rol
    ROL_CHOICES = (
        ('aprendiz', 'Aprendiz'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='aprendiz')
    # Laboratorios a los que puede acceder
    laboratorios_permitidos = models.ManyToManyField('Laboratorio', blank=True)
    
class Laboratorio(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=5, blank=True) # Para guardar el emoji
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class AccesoLaboratorio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    autorizado = models.BooleanField(default=False)
    motivo_denegado = models.CharField(max_length=255, blank=True, null=True)