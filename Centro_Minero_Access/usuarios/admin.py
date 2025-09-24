from django.contrib import admin
from .models import Usuario, Registro


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista principal
    list_display = (
        'nombre', 
        'numero_identificacion', 
        'tipo', 
        'activo', 
        'face_registered', 
        'ambientes_permitidos'  # ← AGREGADO: Para ver rápido en lista
    )
    
    # Filtros en sidebar (derecha)
    list_filter = (
        'tipo', 
        'activo', 
        'face_registered',
        'ambientes_permitidos'  # ← AGREGADO: Filtrar por permisos (básico)
    )
    
    # Búsqueda en lista
    search_fields = ('nombre', 'numero_identificacion')
    
    # Ordenamiento por defecto
    ordering = ('nombre',)
    
    # Campos que aparecen al editar/crear (agrupados para claridad)
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'numero_identificacion', 'tipo')
        }),
        ('Estado y Rostro', {
            'fields': ('activo', 'face_registered', 'face_image')
        }),
        ('Permisos de Acceso', {  # ← NUEVA SECCIÓN: Para el campo nuevo
            'fields': ('ambientes_permitidos',),
            'description': 'Códigos de ambientes separados por coma (ej: sistemas,quimica). Usa "todos" para acceso total.'
        }),
        ('Encoding Facial (Avanzado)', {
            'fields': ('face_encoding',),
            'classes': ('collapse',)  # Oculto por defecto
        }),
    )
    
    # Campos de solo lectura (opcional)
    readonly_fields = ('face_encoding',)


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'tipo',
        'metodo',
        'ambiente',
        'confianza',
        'fecha_hora'
    )
    list_filter = ('tipo', 'metodo', 'ambiente')
    search_fields = ('usuario__nombre', 'usuario__numero_identificacion', 'ambiente')
    ordering = ('-fecha_hora',)

    # Hacer fecha y confianza de solo lectura para evitar manipulación
    readonly_fields = ('fecha_hora', 'confianza')