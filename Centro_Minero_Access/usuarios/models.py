from django.db import models
import os

class Usuario(models.Model):
    TIPO_USUARIO = [
        ('instructor', 'Instructor'),
        ('aprendiz', 'Aprendiz'),
        ('administrativo', 'Administrativo'),
        ('visitante', 'Visitante'),
        ('restringido', 'Restringido'),
    ]

    carnet = models.CharField(max_length=8, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO)
    activo = models.BooleanField(default=True)
    
    # Nuevos campos para reconocimiento facial
    face_image = models.ImageField(upload_to='faces/users/', blank=True, null=True, verbose_name="Imagen Facial")
    face_encoding = models.TextField(blank=True, null=True, verbose_name="Codificación Facial")
    face_registered = models.BooleanField(default=False, verbose_name="Rostro Registrado")
    
    def __str__(self):
        return f"{self.nombre} ({self.carnet})"
    
    def get_face_image_path(self):
        """Retorna la ruta completa de la imagen facial"""
        if self.face_image:
            return self.face_image.path
        return None

class Registro(models.Model):
    """Modelo para registrar los accesos de los usuarios."""
    TIPO_ACCESO = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
    ]
    
    METODO_ACCESO = [
        ('facial', 'Reconocimiento Facial'),
        ('manual', 'Acceso Manual'),
        ('carnet', 'Tarjeta/Carnet'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO_ACCESO)
    metodo = models.CharField(max_length=20, choices=METODO_ACCESO, default='manual')
    ambiente = models.CharField(max_length=50, blank=True, null=True)
    confianza = models.FloatField(blank=True, null=True, verbose_name="Confianza del Reconocimiento")

    def __str__(self):
        return f"{self.usuario.nombre} - {self.tipo} ({self.fecha_hora})"