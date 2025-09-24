from django.contrib import admin
from .models import Usuario, Registro


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'tipo_identificacion',  # <-- Agrega esta línea
        'numero_identificacion',
        'nombre',
        'tipo',
        'activo',
        'face_registered'
    )
    list_filter = ('tipo_identificacion', 'tipo', 'activo', 'face_registered')
    search_fields = ('numero_identificacion', 'nombre')
    ordering = ('nombre',)

    readonly_fields = ('face_registered',)

    fieldsets = (
        ("Información Personal", {
            "fields": ('tipo_identificacion', 'numero_identificacion', 'nombre', 'tipo', 'activo')
        }),
        ("Reconocimiento Facial", {
            "fields": ('face_image', 'face_encoding', 'face_registered'),
            "classes": ('collapse',),
        }),
    )


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