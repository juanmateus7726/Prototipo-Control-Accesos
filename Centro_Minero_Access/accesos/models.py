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
    # Opciones para laboratorio
    LABORATORIO_CHOICES = [
        ('sistemas', 'Laboratorio de Sistemas'),
        ('quimica', 'Laboratorio de Química Aplicada'),
        ('carbones', 'Laboratorio de Carbones'),
        ('biotecnologia', 'Laboratorio de Biotecnología'),
        ('beneficios', 'Lab. Beneficios Minerales'),
        ('aguas', 'Laboratorio de Aguas'),
        ('suelos', 'Laboratorio de Suelos'),
        ('abc_maquinaria', 'Ambiente ABC - Maquinaria Pesada'),
        ('bilinguismo', 'Ambiente de Bilingüismo'),
        ('minas_didacticas', 'Minas Didácticas'),
    ]
    
    # Opciones para método de acceso
    METODO_CHOICES = [
        ('carnet_manual', 'Carnet Manual'),
        ('reconocimiento_facial', 'Reconocimiento Facial'),
        ('tarjeta_rfid', 'Tarjeta RFID'),
        ('huella_digital', 'Huella Digital'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    laboratorio = models.CharField(max_length=50, choices=LABORATORIO_CHOICES)
    metodo = models.CharField(max_length=30, choices=METODO_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    acceso_permitido = models.BooleanField(default=False)
    razon_denegacion = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.laboratorio} - {self.fecha_hora}"