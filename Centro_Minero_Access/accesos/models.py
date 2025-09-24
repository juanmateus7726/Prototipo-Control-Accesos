from django.db import models
from usuarios.models import Usuario


class Acceso(models.Model):
    # Opciones para laboratorio
    AMBIENTE_CHOICES = [
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
        ('manual', 'Acceso Manual'),
        ('reconocimiento_facial', 'Reconocimiento Facial'),
        ('huella_dactilar', 'Huella Dactilar'), # Futuro
        ('tarjeta_rfid', 'Tarjeta RFID'), # Futuro
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ambiente = models.CharField(max_length=50, choices=AMBIENTE_CHOICES)
    metodo = models.CharField(max_length=30, choices=METODO_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    acceso_permitido = models.BooleanField(default=False)
    razon_denegacion = models.CharField(max_length=200, blank=True)
    confianza = models.FloatField(null=True, blank=True, default=None)
    
    def __str__(self):
        return f"{self.usuario} - {self.ambiente} - {self.fecha_hora}"
    
    class Meta:
        verbose_name = "Acceso"
        verbose_name_plural = "Accesos"
        ordering = ['-fecha_hora']