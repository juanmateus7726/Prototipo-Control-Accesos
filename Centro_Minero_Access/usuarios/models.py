from django.db import models
from django.contrib.auth.models import Group
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
    
    numero_identificacion = models.CharField(
        max_length=10,
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
    
    # --------------------------
    # Campos existentes de reconocimiento facial
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

    # --------------------------
    # SISTEMA DE PERMISOS MEJORADO (MIGRACIÓN GRADUAL)
    # --------------------------
    
    # Campo existente (mantener para compatibilidad)
    ambientes_permitidos = models.TextField(
        default='sistemas',
        blank=True,
        verbose_name="Ambientes Permitidos (Legacy)",
        help_text="Códigos de ambientes separados por coma. Escribe 'todos' para acceso total."
    )
    
    # NUEVOS CAMPOS para sistema de permisos mejorado
    grupos = models.ManyToManyField(
        Group, 
        blank=True, 
        related_name='usuarios',
        verbose_name="Grupos de Permisos"
    )
    
    ambientes_directos = models.ManyToManyField(
        'ambientes.Ambiente',  # Referencia al modelo Ambiente
        blank=True,
        related_name='usuarios_permitidos',
        verbose_name="Ambientes Permitidos (Nuevo Sistema)",
        help_text="Ambientes a los que este usuario tiene acceso directo"
    )

    def __str__(self):
        return f"{self.nombre} ({self.numero_identificacion})"

    def is_complete(self):
        return self.activo and self.face_registered

    def get_face_image_path(self):
        if self.face_image:
            return self.face_image.path
        return None

    def has_face_data(self):
        return self.face_registered and bool(self.face_encoding)
    
    # --------------------------
    # MÉTODOS DE VERIFICACIÓN DE PERMISOS (COMPATIBLES)
    # --------------------------
    
    def tiene_permiso_ambiente(self, ambiente):
        """
        Verifica si el usuario tiene permiso para un ambiente específico.
        Prioriza el nuevo sistema, luego fallback al sistema legacy.
        """
        # 1. Verificar nuevo sistema (ambientes_directos)
        if self.ambientes_directos.filter(id=ambiente.id).exists():
            return True
        
        # 2. Verificar nuevo sistema (grupos)
        if self.grupos.exists():
            # Aquí puedes agregar lógica de permisos por grupos si la necesitas
            pass
        
        # 3. Fallback al sistema legacy (ambientes_permitidos)
        return self._tiene_permiso_legacy(ambiente)
    
    def _tiene_permiso_legacy(self, ambiente):
        """Método para compatibilidad con el sistema legacy"""
        if not self.ambientes_permitidos:
            return False
            
        permisos_raw = self.ambientes_permitidos.lower().split(',')
        permisos = [p.strip() for p in permisos_raw if p.strip()]
        
        if 'todos' in permisos:
            return True
            
        # Buscar por código del ambiente
        if ambiente.codigo.lower() in permisos:
            return True
            
        # Buscar por nombre del ambiente (para compatibilidad)
        if ambiente.nombre.lower() in [p.lower() for p in permisos]:
            return True
            
        return False
    
    def obtener_ambientes_permitidos(self):
        """
        Retorna todos los ambientes a los que tiene acceso (nuevo sistema + legacy)
        """
        from ambientes.models import Ambiente  # Import aquí para evitar circular imports
        
        ambientes = set()
        
        # 1. Ambientes del nuevo sistema
        ambientes.update(self.ambientes_directos.all())
        
        # 2. Ambientes del sistema legacy
        if self.ambientes_permitidos:
            permisos_raw = self.ambientes_permitidos.lower().split(',')
            permisos = [p.strip() for p in permisos_raw if p.strip()]
            
            if 'todos' in permisos:
                ambientes.update(Ambiente.objects.all())
            else:
                for permiso in permisos:
                    # Buscar por código
                    ambientes_codigo = Ambiente.objects.filter(codigo__iexact=permiso)
                    ambientes.update(ambientes_codigo)
                    
                    # Buscar por nombre (compatibilidad)
                    ambientes_nombre = Ambiente.objects.filter(nombre__icontains=permiso)
                    ambientes.update(ambientes_nombre)
        
        return list(ambientes)
    
    def migrar_permisos_automaticamente(self):
        """
        Migra automáticamente los permisos del sistema legacy al nuevo sistema
        """
        if self.ambientes_permitidos and not self.ambientes_directos.exists():
            from ambientes.models import Ambiente
            
            permisos_raw = self.ambientes_permitidos.lower().split(',')
            permisos = [p.strip() for p in permisos_raw if p.strip()]
            
            if 'todos' in permisos:
                self.ambientes_directos.set(Ambiente.objects.all())
            else:
                for permiso in permisos:
                    try:
                        # Intentar por código
                        ambiente = Ambiente.objects.get(codigo__iexact=permiso)
                        self.ambientes_directos.add(ambiente)
                    except Ambiente.DoesNotExist:
                        try:
                            # Intentar por nombre
                            ambiente = Ambiente.objects.get(nombre__iexact=permiso)
                            self.ambientes_directos.add(ambiente)
                        except Ambiente.DoesNotExist:
                            # Si no existe, continuar
                            continue
            
            self.save()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['nombre']

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