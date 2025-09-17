from django.db import models

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

    def __str__(self):
        # 🔹 Mostrará "Nombre (Carnet)"
        return f"{self.nombre} ({self.carnet})"

class Registro(models.Model):
    """Modelo para registrar los accesos de los usuarios."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=[('Entrada', 'Entrada'), ('Salida', 'Salida')])

    def __str__(self):
        return f"{self.usuario.nombre} - {self.tipo} ({self.fecha_hora})"