# usuarios/models.py
from django.db import models
from django.contrib.auth.models import Group


# =====================================
#  MODELO: Usuario
# =====================================
class Usuario(models.Model):
    # ---- Tipos de usuario ----
    TIPO_USUARIO = [
        ('instructor', 'Instructor'),
        ('aprendiz', 'Aprendiz'),
        ('administrativo', 'Administrativo'),
        ('visitante', 'Visitante'),
        ('restringido', 'Restringido'),
    ]

    # ---- Tipos de identificación ----
    TIPO_IDENTIFICACION = [
        ('cc', 'Cédula de Ciudadanía'),
        ('ce', 'Cédula de Extranjería'),
        ('pa', 'Pasaporte'),
        ('ti', 'Tarjeta de Identidad'),
    ]

    # ==== Datos personales ====
    tipo_identificacion = models.CharField(
        max_length=2,
        choices=TIPO_IDENTIFICACION,
        default='cc',
        verbose_name="Tipo de Identificación"
    )

    numero_identificacion = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Identificación"
    )

    nombre = models.CharField(
        max_length=150,
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

    # ==== Reconocimiento Facial ====
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

    # ==== Permisos (Legacy + Nuevo) ====
    ambientes_permitidos = models.TextField(
        default='',
        blank=True,
        verbose_name="Ambientes Permitidos (Legacy)",
        help_text="Códigos de ambientes separados por coma. Escribe 'todos' para acceso total."
    )

    grupos = models.ManyToManyField(
        Group,
        blank=True,
        related_name='usuarios',
        verbose_name="Grupos de Permisos"
    )

    ambientes_directos = models.ManyToManyField(
        'ambientes.Ambiente',
        blank=True,
        related_name='usuarios_directos',
        verbose_name="Ambientes Permitidos (Nuevo Sistema)"
    )

    # ==== Métodos ====
    def __str__(self):
        return f"{self.nombre} ({self.numero_identificacion})"

    def is_complete(self):
        """Verifica si el usuario está activo y tiene rostro registrado."""
        return self.activo and self.face_registered

    def has_face_data(self):
        """Indica si tiene datos faciales cargados."""
        return self.face_registered and bool(self.face_encoding)

    def tiene_permiso_ambiente(self, ambiente):
        """
        Verifica si el usuario tiene acceso al ambiente.
        Primero revisa el nuevo sistema, luego el legacy.
        """
        # Nuevo sistema: acceso directo
        if self.ambientes_directos.filter(pk=ambiente.pk).exists():
            return True

        # Nuevo sistema: acceso por grupos (extensible)
        if self.grupos.exists():
            # Aquí se podría agregar lógica de permisos por grupo
            pass

        # Legacy
        return self._tiene_permiso_legacy(ambiente)

    def _tiene_permiso_legacy(self, ambiente):
        """Verifica permisos usando el sistema legacy."""
        if not self.ambientes_permitidos:
            return False

        permisos = [p.strip().lower() for p in self.ambientes_permitidos.split(',') if p.strip()]

        if 'todos' in permisos:
            return True

        if ambiente.codigo.lower() in permisos or ambiente.nombre.lower() in permisos:
            return True

        return False

    def obtener_ambientes_permitidos(self):
        """Devuelve todos los ambientes que el usuario puede usar (nuevo + legacy)."""
        from ambientes.models import Ambiente
        ambientes = set()

        # Nuevo sistema
        ambientes.update(self.ambientes_directos.all())

        # Legacy
        if self.ambientes_permitidos:
            permisos = [p.strip().lower() for p in self.ambientes_permitidos.split(',') if p.strip()]
            if 'todos' in permisos:
                ambientes.update(Ambiente.objects.all())
            else:
                ambientes.update(Ambiente.objects.filter(codigo__in=permisos))
                ambientes.update(Ambiente.objects.filter(nombre__in=permisos))

        return list(ambientes)

    def migrar_permisos_automaticamente(self):
        """
        Migra automáticamente los ambientes del sistema legacy al nuevo sistema.
        """
        from ambientes.models import Ambiente
        if self.ambientes_permitidos and not self.ambientes_directos.exists():
            permisos = [p.strip().lower() for p in self.ambientes_permitidos.split(',') if p.strip()]
            if 'todos' in permisos:
                self.ambientes_directos.set(Ambiente.objects.all())
            else:
                for permiso in permisos:
                    ambiente = Ambiente.objects.filter(codigo__iexact=permiso).first() or \
                               Ambiente.objects.filter(nombre__iexact=permiso).first()
                    if ambiente:
                        self.ambientes_directos.add(ambiente)
            self.save()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['nombre']


# =====================================
#  MODELO: Registro de Accesos
# =====================================
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
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ambiente/Laboratorio"
    )

    confianza = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Nivel de Confianza (%)"
    )

    def __str__(self):
        return f"{self.usuario.nombre} - {self.tipo} ({self.fecha_hora.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = "Registro de Acceso"
        verbose_name_plural = "Registros de Acceso"
        ordering = ['-fecha_hora']
