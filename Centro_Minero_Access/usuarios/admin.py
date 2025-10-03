# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import Usuario, Registro


# ================================
#  ADMIN: Usuario
# ================================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Usuario.
    Incluye búsqueda, filtros, campos organizados y vista previa de la imagen facial.
    """
    list_display = [
        'nombre',
        'numero_identificacion',
        'tipo',
        'activo',
        'face_registered',
        'preview_face'
    ]
    list_filter = [
        'tipo',
        'activo',
        'face_registered'
    ]
    search_fields = [
        'nombre',
        'numero_identificacion'
    ]
    filter_horizontal = ['grupos', 'ambientes_directos']

    fieldsets = (
        ('Información Personal', {
            'fields': (
                'tipo_identificacion',
                'numero_identificacion',
                'nombre',
                'tipo',
                'activo'
            )
        }),
        ('Sistema de Permisos - Nuevo', {
            'fields': ('grupos', 'ambientes_directos'),
            'description': 'Asigne los grupos y ambientes permitidos usando el nuevo sistema de permisos.'
        }),
        ('Sistema de Permisos - Legacy', {
            'fields': ('ambientes_permitidos',),
            'description': 'Campo para compatibilidad con el sistema antiguo. Se migrará automáticamente al nuevo sistema si está vacío.'
        }),
        ('Reconocimiento Facial', {
            'fields': (
                'face_image',
                'preview_face',
                'face_registered'
            ),
            'description': 'Suba la imagen facial. La vista previa aparecerá al seleccionar la foto antes de guardar.'
        }),
    )

    readonly_fields = ['preview_face']

    def preview_face(self, obj):
        """
        Muestra una vista previa de la imagen facial si existe.
        """
        if obj.face_image:
            return format_html(
                '<img id="face-preview" src="{}" style="max-height: 150px; border-radius: 12px; '
                'border:2px solid #4CAF50; box-shadow:0 4px 10px rgba(0,0,0,0.2); padding:3px; margin-top:6px;"/>',
                obj.face_image.url
            )
        return format_html(
            '<img id="face-preview" style="display:none; max-height:150px; border-radius:12px; '
            'border:2px dashed #ccc; padding:3px; margin-top:6px;"/>'
        )

    preview_face.short_description = "Vista previa"

    def save_model(self, request, obj, form, change):
        """
        Sobrescribe el guardado para migrar permisos legacy al nuevo sistema automáticamente.
        """
        super().save_model(request, obj, form, change)
        if obj.ambientes_permitidos and not obj.ambientes_directos.exists():
            obj.migrar_permisos_automaticamente()

    # 👉 Incluir el archivo JS para vista previa en tiempo real
    class Media:
        js = ('admin/js/preview_face.js',)


# ================================
#  ADMIN: Registro
# ================================
@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    """
    Panel de administración para el histórico de accesos.
    Permite filtrar por usuario, tipo de acceso, método y fecha.
    """
    list_display = [
        'usuario',
        'tipo',
        'metodo',
        'ambiente',
        'confianza',
        'fecha_hora'
    ]
    list_filter = [
        'tipo',
        'metodo',
        'ambiente',
        'fecha_hora'
    ]
    search_fields = [
        'usuario__nombre',
        'usuario__numero_identificacion',
        'ambiente'
    ]
    ordering = ['-fecha_hora']


# ================================
#  ADMIN: Group
# ================================
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
