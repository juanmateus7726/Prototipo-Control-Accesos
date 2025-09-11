from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    carnet = models.CharField(max_length=8, unique=True)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ("instructor", "Instructor"),
            ("aprendiz", "Aprendiz"),
            ("administrativo", "Administrativo"),
            ("visitante", "Visitante"),
            ("restringido", "Restringido")
        ]
    )
    activo = models.BooleanField(default=True)
    areas_permitidas = models.JSONField(default=list) # Lista de ambientes permitidos
    
    def __str__(self):
        return f"{self.nombre} ({self.carnet})"
    

class Acceso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    laboratorio = models.CharField(max_length=50, default='Laboratorio X')
    metodo = models.CharField(max_length=30, default='manual')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.laboratorio} - {self.fecha_hora}"