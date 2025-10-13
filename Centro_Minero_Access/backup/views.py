import os
import shutil
import zipfile
import subprocess
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse, Http404

# ========================================
# CONFIGURACIÓN: Ruta de MySQL
# ========================================
# Cambia esta ruta según tu instalación de MySQL
MYSQL_BIN_PATH = r"C:\Program Files\MySQL\MySQL Server 9.0\bin"

# Si usas XAMPP, usa esta ruta:
# MYSQL_BIN_PATH = r"C:\xampp\mysql\bin"

# Si usas WAMP, usa una ruta similar a:
# MYSQL_BIN_PATH = r"C:\wamp64\bin\mysql\mysql8.0.31\bin"

MYSQLDUMP_PATH = os.path.join(MYSQL_BIN_PATH, "mysqldump.exe")
MYSQL_PATH = os.path.join(MYSQL_BIN_PATH, "mysql.exe")


def find_mysql_path():
    """Intenta encontrar automáticamente la ruta de MySQL"""
    possible_paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files\MySQL\MySQL Server 5.7\bin",
        r"C:\xampp\mysql\bin",
        r"C:\wamp64\bin\mysql\mysql8.0.31\bin",
        r"C:\wamp64\bin\mysql\mysql8.0.30\bin",
        r"C:\wamp64\bin\mysql\mysql8.0.29\bin",
    ]
    
    for path in possible_paths:
        mysqldump = os.path.join(path, "mysqldump.exe")
        if os.path.exists(mysqldump):
            return path
    
    return None


@login_required
def backup_list(request):
    """Lista todos los backups disponibles"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    # Crear directorio si no existe
    os.makedirs(backup_dir, exist_ok=True)
    
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.startswith('backup_') and filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                
                if os.path.isfile(filepath):
                    try:
                        stat = os.stat(filepath)
                        backups.append({
                            'nombre': filename,
                            'fecha': datetime.fromtimestamp(stat.st_mtime),
                            'tamaño': format_size(stat.st_size)
                        })
                    except Exception as e:
                        print(f"Error al leer archivo {filename}: {e}")
    
    backups.sort(key=lambda x: x['fecha'], reverse=True)
    
    return render(request, 'backup/backup_list.html', {'backups': backups})


@login_required
def crear_backup(request):
    """Crea un nuevo backup de la base de datos MySQL en formato ZIP"""
    # Verificar que MySQL esté disponible
    mysql_path = MYSQL_BIN_PATH
    if not os.path.exists(MYSQLDUMP_PATH):
        # Intentar encontrar automáticamente
        mysql_path = find_mysql_path()
        if mysql_path is None:
            messages.error(
                request, 
                '✗ MySQL no encontrado. Por favor, configura MYSQL_BIN_PATH en backup/views.py'
            )
            return redirect('backup:backup_list')
        mysqldump = os.path.join(mysql_path, "mysqldump.exe")
    else:
        mysqldump = MYSQLDUMP_PATH
    
    # Obtener configuración de la base de datos
    db_config = settings.DATABASES['default']
    db_engine = db_config['ENGINE']
    
    if 'mysql' not in db_engine.lower():
        messages.error(request, '✗ Este sistema de backup solo funciona con MySQL')
        return redirect('backup:backup_list')
    
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config['PASSWORD']
    db_host = db_config.get('HOST', 'localhost')
    db_port = db_config.get('PORT', '3306')
    
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sql_filename = f'backup_{timestamp}.sql'
    zip_filename = f'backup_{timestamp}.zip'
    
    sql_path = os.path.join(backup_dir, sql_filename)
    zip_path = os.path.join(backup_dir, zip_filename)
    
    try:
        # Comando mysqldump con ruta completa
        mysqldump_cmd = [
            mysqldump,
            f'--user={db_user}',
            f'--password={db_password}',
            f'--host={db_host}',
            f'--port={db_port}',
            '--single-transaction',
            '--quick',
            '--lock-tables=false',
            db_name
        ]
        
        # Ejecutar mysqldump
        with open(sql_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                mysqldump_cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if result.returncode != 0:
            error_msg = result.stderr
            if os.path.exists(sql_path):
                os.remove(sql_path)
            raise Exception(f"Error en mysqldump: {error_msg}")
        
        if not os.path.exists(sql_path) or os.path.getsize(sql_path) == 0:
            raise Exception("El archivo SQL está vacío o no se creó")
        
        # Crear ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            zipf.write(sql_path, sql_filename)
        
        # Limpiar SQL temporal
        if os.path.exists(sql_path):
            os.remove(sql_path)
        
        if not os.path.exists(zip_path):
            raise Exception("El archivo ZIP no se creó correctamente")
        
        limpiar_backups_antiguos(backup_dir, limite=10)
        
        size = os.path.getsize(zip_path)
        size_mb = size / (1024 * 1024)
        
        messages.success(request, f'✓ Backup MySQL creado exitosamente: {zip_filename} ({size_mb:.2f} MB)')
        
    except Exception as e:
        messages.error(request, f'✗ Error al crear backup: {str(e)}')
        for temp_file in [sql_path, zip_path]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    return redirect('backup:backup_list')


@login_required
def descargar_backup(request, filename):
    """Descarga un archivo de backup ZIP"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    if not filename.startswith('backup_') or not filename.endswith('.zip'):
        messages.error(request, '✗ Nombre de archivo no válido')
        return redirect('backup:backup_list')
    
    if not os.path.exists(filepath):
        messages.error(request, f'✗ Archivo no encontrado: {filename}')
        return redirect('backup:backup_list')
    
    if not os.path.isfile(filepath):
        messages.error(request, '✗ La ruta no corresponde a un archivo')
        return redirect('backup:backup_list')
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zipf:
            zipf.testzip()
        
        file = open(filepath, 'rb')
        response = FileResponse(
            file,
            as_attachment=True,
            filename=filename
        )
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except zipfile.BadZipFile:
        messages.error(request, '✗ El archivo ZIP está corrupto')
        return redirect('backup:backup_list')
    except Exception as e:
        messages.error(request, f'✗ Error al descargar: {str(e)}')
        return redirect('backup:backup_list')


@login_required
def eliminar_backup(request, filename):
    """Elimina un archivo de backup ZIP"""
    if request.method == 'POST':
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if os.path.exists(filepath) and filename.startswith('backup_') and filename.endswith('.zip'):
            try:
                os.remove(filepath)
                messages.success(request, f'✓ Backup eliminado: {filename}')
            except Exception as e:
                messages.error(request, f'✗ Error al eliminar: {str(e)}')
        else:
            messages.error(request, '✗ Backup no encontrado o formato inválido')
        
        return redirect('backup:backup_list')
    
    return redirect('backup:backup_list')


@login_required
def restaurar_backup(request, filename):
    """Restaura la base de datos MySQL desde un archivo ZIP"""
    if request.method == 'POST':
        # Verificar que MySQL esté disponible
        mysql_path = MYSQL_BIN_PATH
        if not os.path.exists(MYSQL_PATH):
            mysql_path = find_mysql_path()
            if mysql_path is None:
                messages.error(
                    request,
                    '✗ MySQL no encontrado. Por favor, configura MYSQL_BIN_PATH en backup/views.py'
                )
                return redirect('backup:backup_list')
            mysql_exe = os.path.join(mysql_path, "mysql.exe")
        else:
            mysql_exe = MYSQL_PATH
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        zip_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(zip_path) or not filename.endswith('.zip'):
            messages.error(request, '✗ Archivo de backup no válido')
            return redirect('backup:backup_list')
        
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config.get('HOST', 'localhost')
        db_port = db_config.get('PORT', '3306')
        
        temp_dir = os.path.join(backup_dir, 'temp_restore')
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extraer ZIP
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                sql_files = [f for f in zipf.namelist() if f.endswith('.sql')]
                
                if not sql_files:
                    messages.error(request, '✗ No se encontró archivo SQL en el backup')
                    return redirect('backup:backup_list')
                
                zipf.extract(sql_files[0], temp_dir)
                sql_path = os.path.join(temp_dir, sql_files[0])
            
            # Cerrar conexiones Django
            from django.db import connections
            for conn in connections.all():
                conn.close()
            
            # Comando mysql con ruta completa
            mysql_cmd = [
                mysql_exe,
                f'--user={db_user}',
                f'--password={db_password}',
                f'--host={db_host}',
                f'--port={db_port}',
                db_name
            ]
            
            # Restaurar
            with open(sql_path, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    mysql_cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            shutil.rmtree(temp_dir)
            
            if result.returncode != 0:
                error_msg = result.stderr
                raise Exception(f"Error al restaurar: {error_msg}")
            
            messages.success(request, f'✓ Base de datos restaurada exitosamente desde: {filename}')
            messages.warning(request, '⚠️ Por favor, cierra sesión y vuelve a iniciar para aplicar todos los cambios')
            
        except Exception as e:
            messages.error(request, f'✗ Error al restaurar el backup: {str(e)}')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        return redirect('backup:backup_list')
    
    return redirect('backup:backup_list')


def limpiar_backups_antiguos(backup_dir, limite=10):
    """Mantiene solo los últimos N backups"""
    archivos = []
    
    for filename in os.listdir(backup_dir):
        if filename.startswith('backup_') and filename.endswith('.zip'):
            filepath = os.path.join(backup_dir, filename)
            if os.path.isfile(filepath):
                archivos.append((filepath, os.path.getmtime(filepath)))
    
    archivos.sort(key=lambda x: x[1], reverse=True)
    
    for filepath, _ in archivos[limite:]:
        try:
            os.remove(filepath)
            print(f"Backup antiguo eliminado: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Error al eliminar {filepath}: {e}")


def format_size(bytes):
    """Formatea el tamaño del archivo en unidades legibles"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"