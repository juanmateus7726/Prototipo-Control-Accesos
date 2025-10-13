import os
import subprocess
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Crea una copia de seguridad de la base de datos MySQL'

    def handle(self, *args, **options):
        # Obtener configuración de la base de datos
        db_config = settings.DATABASES['default']
        db_engine = db_config['ENGINE']
        
        # Verificar que sea MySQL
        if 'mysql' not in db_engine.lower():
            self.stdout.write(
                self.style.ERROR('✗ Este comando solo funciona con MySQL')
            )
            return
        
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config.get('HOST', 'localhost')
        db_port = db_config.get('PORT', '3306')
        
        # Crear carpeta de backups si no existe
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Crear nombre del backup con fecha y hora
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sql_filename = f'backup_{timestamp}.sql'
        zip_filename = f'backup_{timestamp}.zip'
        
        sql_path = os.path.join(backup_dir, sql_filename)
        zip_path = os.path.join(backup_dir, zip_filename)
        
        try:
            # Comando mysqldump
            mysqldump_cmd = [
                'mysqldump',
                f'--user={db_user}',
                f'--password={db_password}',
                f'--host={db_host}',
                f'--port={db_port}',
                '--single-transaction',
                '--quick',
                '--lock-tables=false',
                db_name
            ]
            
            # Ejecutar mysqldump y guardar en archivo SQL
            with open(sql_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    mysqldump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode != 0:
                if os.path.exists(sql_path):
                    os.remove(sql_path)
                raise Exception(f"Error en mysqldump: {result.stderr}")
            
            # Crear archivo ZIP con compresión
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                zipf.write(sql_path, sql_filename)
            
            # Eliminar archivo SQL temporal
            if os.path.exists(sql_path):
                os.remove(sql_path)
            
            # Calcular tamaño
            size = os.path.getsize(zip_path)
            size_mb = size / (1024 * 1024)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Backup creado exitosamente: {zip_filename} ({size_mb:.2f} MB)')
            )
            
            # Limpiar backups antiguos (mantener solo los últimos 10)
            self.cleanup_old_backups(backup_dir)
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('✗ mysqldump no encontrado. Verifica que MySQL esté en el PATH del sistema')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error al crear backup: {str(e)}')
            )
    
    def cleanup_old_backups(self, backup_dir, keep=10):
        """Mantiene solo los últimos N backups"""
        backups = []
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('backup_') and filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                backups.append((filepath, os.path.getmtime(filepath)))
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Eliminar archivos antiguos
        for filepath, _ in backups[keep:]:
            try:
                os.remove(filepath)
                self.stdout.write(
                    self.style.WARNING(f'  Backup antiguo eliminado: {os.path.basename(filepath)}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error al eliminar {filepath}: {e}')
                )