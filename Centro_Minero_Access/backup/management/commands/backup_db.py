import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Crea una copia de seguridad de la base de datos SQLite'

    def handle(self, *args, **options):
        # Obtener la ruta de la base de datos
        db_path = settings.DATABASES['default']['NAME']
        
        # Crear carpeta de backups si no existe
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Crear nombre del backup con fecha y hora
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}.sqlite3'
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            # Copiar la base de datos
            shutil.copy2(db_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Backup creado exitosamente: {backup_name}')
            )
            
            # Limpiar backups antiguos (mantener solo los últimos 10)
            self.cleanup_old_backups(backup_dir)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error al crear backup: {str(e)}')
            )
    
    def cleanup_old_backups(self, backup_dir, keep=10):
        """Mantiene solo los últimos N backups"""
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.startswith('backup_')],
            reverse=True
        )
        
        for old_backup in backups[keep:]:
            os.remove(os.path.join(backup_dir, old_backup))
            self.stdout.write(
                self.style.WARNING(f'  Backup antiguo eliminado: {old_backup}')
            )