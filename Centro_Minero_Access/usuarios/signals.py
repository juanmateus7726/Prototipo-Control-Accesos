import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Usuario


@receiver(post_delete, sender=Usuario)
def eliminar_imagen_usuario(sender, instance, **kwargs):
    """Elimina la imagen facial del usuario al borrarlo."""
    if instance.face_image:
        if os.path.isfile(instance.face_image.path):
            os.remove(instance.face_image.path)


@receiver(pre_save, sender=Usuario)
def eliminar_imagen_anterior(sender, instance, **kwargs):
    """
    Si se actualiza la imagen facial de un usuario,
    elimina la anterior del disco para no acumular archivos.
    """
    if not instance.pk:
        return False  # Es un nuevo usuario, no hay imagen previa

    try:
        old_instance = Usuario.objects.get(pk=instance.pk)
    except Usuario.DoesNotExist:
        return False

    # Si cambia la imagen facial
    if old_instance.face_image and old_instance.face_image != instance.face_image:
        if os.path.isfile(old_instance.face_image.path):
            os.remove(old_instance.face_image.path)
