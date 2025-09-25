# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'numero_identificacion', 'tipo', 'activo', 'face_registered']
    list_filter = ['tipo', 'activo', 'face_registered']
    search_fields = ['nombre', 'numero_identificacion']
    filter_horizontal = ['grupos', 'ambientes_directos']  # Para selección fácil
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('tipo_identificacion', 'numero_identificacion', 'nombre', 'tipo', 'activo')
        }),
        ('Sistema de Permisos - Nuevo', {
            'fields': ('grupos', 'ambientes_directos'),
            'description': 'Sistema nuevo de permisos (recomendado)'
        }),
        ('Sistema de Permisos - Legacy', {
            'fields': ('ambientes_permitidos',),
            'description': 'Sistema antiguo (mantener para compatibilidad)'
        }),
        ('Reconocimiento Facial', {
            'fields': ('face_image', 'face_encoding', 'face_registered')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Migrar automáticamente al guardar desde admin"""
        super().save_model(request, obj, form, change)
        if obj.ambientes_permitidos and not obj.ambientes_directos.exists():
            obj.migrar_permisos_automaticamente()

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)