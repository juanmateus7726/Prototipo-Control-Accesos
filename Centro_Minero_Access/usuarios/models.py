from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import os


class Usuario(models.Model):
    TIPO_USUARIO = [
        ('instructor', 'Instructor'),
        ('aprendiz', 'Aprendiz'),
        ('administrativo', 'Administrativo'),
        ('visitante', 'Visitante'),
        ('restringido', 'Restringido'),
    ]

    TIPO_IDENTIFICACION = [
        ('cc', 'Cédula de Ciudadanía'),
        ('ce', 'Cédula de Extranjería'),
        ('pa', 'Pasaporte'),
        ('ti', 'Tarjeta de Identidad'),
    ]

    tipo_identificacion = models.CharField(
        max_length=2,
        choices=TIPO_IDENTIFICACION,
        default='cc',
        verbose_name="Tipo de Identificación"
    )
    # Cambiamos 'carnet' por 'numero_identificacion'
    numero_identificacion = models.CharField(
        max_length=10,  # Un largo suficiente para diferentes tipos de documentos
        unique=False,
        null=True,
        verbose_name="Número de Identificación"
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre Completo"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO,
        verbose_name="Tipo de Usuario"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Usuario Activo"
    )
    
    def is_complete(self):
        return self.activo and self.face_registered

    # --------------------------
    # Reconocimiento Facial
    # --------------------------
    face_image = models.ImageField(
        upload_to='faces/users/',
        blank=True,
        null=True,
        verbose_name="Imagen Facial"
    )
    face_encoding = models.TextField(
        blank=True,
        null=True,
        verbose_name="Codificación Facial (JSON)"
    )
    face_registered = models.BooleanField(
        default=False,
        verbose_name="Rostro Registrado"
    )

    def __str__(self):
        return f"{self.nombre} ({self.numero_identificacion})"

    def get_face_image_path(self):
        """
        Retorna la ruta absoluta de la imagen facial si existe.
        """
        if self.face_image:
            return self.face_image.path
        return None

    def has_face_data(self):
        """
        Retorna True si el usuario tiene rostro registrado (imagen + encoding).
        """
        return self.face_registered and bool(self.face_encoding)
    
    ambientes_permitidos = models.TextField(
        default='sistemas',  # Por defecto, permite solo "sistemas" para prototipo
        blank=True,
        verbose_name="Ambientes Permitidos",
        help_text="Códigos de ambientes separados por coma (ej: sistemas,quimica,carbones). Escribe 'todos' para acceso total."
    )


class Registro(models.Model):
    """Histórico de accesos de los usuarios."""

    TIPO_ACCESO = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
    ]

    METODO_ACCESO = [
        ('facial', 'Reconocimiento Facial'),
        ('manual', 'Acceso Manual'),
        ('carnet', 'Tarjeta/Carnet'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="registros"
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_ACCESO,
        verbose_name="Tipo de Acceso"
    )
    metodo = models.CharField(
        max_length=20,
        choices=METODO_ACCESO,
        default='manual',
        verbose_name="Método de Acceso"
    )
    ambiente = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ambiente/Laboratorio"
    )
    confianza = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nivel de Confianza"
    )

    def __str__(self):
        return f"{self.usuario.nombre} - {self.tipo} ({self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')})"

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = "Registro de Acceso"
        verbose_name_plural = "Registros de Acceso"