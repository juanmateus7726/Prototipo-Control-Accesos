import os
import shutil
import zipfile
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse, Http404


@login_required
def backup_list(request):
    """Lista todos los backups disponibles"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    # Crear directorio si no existe
    os.makedirs(backup_dir, exist_ok=True)
    
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            # Ahora buscamos archivos .zip en lugar de .sqlite3
            if filename.startswith('backup_') and filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'nombre': filename,
                    'fecha': datetime.fromtimestamp(stat.st_mtime),
                    'tamaño': format_size(stat.st_size)
                })
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x['fecha'], reverse=True)
    
    return render(request, 'backup/backup_list.html', {'backups': backups})


@login_required
def crear_backup(request):
    """Crea un nuevo backup de la base de datos en formato ZIP"""
    db_path = settings.DATABASES['default']['NAME']
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_filename = f'backup_{timestamp}.sqlite3'
    zip_filename = f'backup_{timestamp}.zip'
    
    # Rutas completas
    temp_db_path = os.path.join(backup_dir, db_filename)
    zip_path = os.path.join(backup_dir, zip_filename)
    
    try:
        # 1. Copiar la base de datos a un archivo temporal
        shutil.copy2(db_path, temp_db_path)
        
        # 2. Crear archivo ZIP con compresión máxima
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            # Agregar la base de datos al ZIP
            zipf.write(temp_db_path, db_filename)
        
        # 3. Eliminar el archivo temporal (sin comprimir)
        os.remove(temp_db_path)
        
        # 4. Limpiar backups antiguos (mantener solo los últimos 10)
        limpiar_backups_antiguos(backup_dir, limite=10)
        
        # Calcular tamaño del archivo
        size = os.path.getsize(zip_path)
        size_mb = size / (1024 * 1024)
        
        messages.success(request, f'✓ Backup creado exitosamente: {zip_filename} ({size_mb:.2f} MB)')
        
    except Exception as e:
        messages.error(request, f'✗ Error al crear backup: {str(e)}')
        # Limpiar archivos temporales en caso de error
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
    
    return redirect('backup:backup_list')


@login_required
def descargar_backup(request, filename):
    """Descarga un archivo de backup ZIP"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    # Validar que el archivo existe y es un ZIP
    if os.path.exists(filepath) and filename.startswith('backup_') and filename.endswith('.zip'):
        response = FileResponse(
            open(filepath, 'rb'),
            as_attachment=True,
            filename=filename,
            content_type='application/zip'
        )
        return response
    else:
        messages.error(request, 'Backup no encontrado')
        raise Http404("Backup no encontrado")


@login_required
def eliminar_backup(request, filename):
    """Elimina un archivo de backup ZIP"""
    if request.method == 'POST':
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        # Validar que es un archivo ZIP válido
        if os.path.exists(filepath) and filename.startswith('backup_') and filename.endswith('.zip'):
            try:
                os.remove(filepath)
                messages.success(request, f'✓ Backup eliminado: {filename}')
            except Exception as e:
                messages.error(request, f'✗ Error al eliminar: {str(e)}')
        else:
            messages.error(request, 'Backup no encontrado o formato inválido')
        
        return redirect('backup:backup_list')


def limpiar_backups_antiguos(backup_dir, limite=10):
    """
    Mantiene solo los últimos N backups y elimina los más antiguos
    """
    archivos = []
    
    # Listar solo archivos .zip
    for filename in os.listdir(backup_dir):
        if filename.startswith('backup_') and filename.endswith('.zip'):
            filepath = os.path.join(backup_dir, filename)
            archivos.append((filepath, os.path.getmtime(filepath)))
    
    # Ordenar por fecha de modificación (más reciente primero)
    archivos.sort(key=lambda x: x[1], reverse=True)
    
    # Eliminar archivos que excedan el límite
    for filepath, _ in archivos[limite:]:
        try:
            os.remove(filepath)
            print(f"Backup antiguo eliminado: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Error al eliminar {filepath}: {e}")


def format_size(bytes):
    """
    Formatea el tamaño del archivo en unidades legibles
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


# ============================================
# FUNCIÓN RESTAURAR BACKUP
# ============================================

@login_required
def restaurar_backup(request, filename):
    """
    Restaura la base de datos desde un archivo ZIP
    IMPORTANTE: Cierra todas las conexiones activas antes de restaurar
    """
    if request.method == 'POST':
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        zip_path = os.path.join(backup_dir, filename)
        
        # Validar archivo
        if not os.path.exists(zip_path) or not filename.endswith('.zip'):
            messages.error(request, '✗ Archivo de backup no válido')
            return redirect('backup:backup_list')
        
        try:
            # Cerrar todas las conexiones de Django a la BD
            from django.db import connections
            for conn in connections.all():
                conn.close()
            
            # Extraer el ZIP
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Buscar el archivo .sqlite3 dentro del ZIP
                db_files = [f for f in zipf.namelist() if f.endswith('.sqlite3')]
                
                if not db_files:
                    messages.error(request, '✗ No se encontró base de datos en el backup')
                    return redirect('backup:backup_list')
                
                # Extraer a un directorio temporal
                temp_dir = os.path.join(backup_dir, 'temp_restore')
                os.makedirs(temp_dir, exist_ok=True)
                
                zipf.extract(db_files[0], temp_dir)
                
                # Ruta de la base de datos actual
                db_path = settings.DATABASES['default']['NAME']
                extracted_db = os.path.join(temp_dir, db_files[0])
                
                # Crear backup de seguridad de la DB actual
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_actual = str(db_path) + f'.before_restore_{timestamp}'
                shutil.copy2(db_path, backup_actual)
                
                # Restaurar la base de datos
                shutil.copy2(extracted_db, db_path)
                
                # Limpiar archivos temporales
                shutil.rmtree(temp_dir)
                
                messages.success(request, f'✓ Base de datos restaurada exitosamente desde: {filename}')
                messages.info(request, f'📁 Respaldo de seguridad creado: {os.path.basename(backup_actual)}')
                messages.warning(request, '⚠️ Por favor, cierra sesión y vuelve a iniciar para aplicar todos los cambios')
            
        except Exception as e:
            messages.error(request, f'✗ Error al restaurar el backup: {str(e)}')
            # Limpiar en caso de error
            temp_dir = os.path.join(backup_dir, 'temp_restore')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        return redirect('backup:backup_list')
    
    return redirect('backup:backup_list')