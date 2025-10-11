import os
import shutil
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
            if filename.startswith('backup_') and filename.endswith('.sqlite3'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'nombre': filename,
                    'fecha': datetime.fromtimestamp(stat.st_mtime),
                    'tamaño': f"{stat.st_size / 1024:.2f} KB"
                })
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x['fecha'], reverse=True)
    
    return render(request, 'backup/backup_list.html', {'backups': backups})

@login_required
def crear_backup(request):
    """Crea un nuevo backup de la base de datos"""
    db_path = settings.DATABASES['default']['NAME']
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.sqlite3'
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2(db_path, backup_path)
        messages.success(request, f'✓ Backup creado exitosamente: {backup_name}')
    except Exception as e:
        messages.error(request, f'✗ Error al crear backup: {str(e)}')
    
    return redirect('backup:backup_list')

@login_required
def descargar_backup(request, filename):
    """Descarga un archivo de backup"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    if os.path.exists(filepath) and filename.startswith('backup_'):
        return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("Backup no encontrado")

@login_required
def eliminar_backup(request, filename):
    """Elimina un archivo de backup"""
    if request.method == 'POST':
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if os.path.exists(filepath) and filename.startswith('backup_'):
            try:
                os.remove(filepath)
                messages.success(request, f'✓ Backup eliminado: {filename}')
            except Exception as e:
                messages.error(request, f'✗ Error al eliminar: {str(e)}')
        else:
            messages.error(request, 'Backup no encontrado')
    
    return redirect('backup:backup_list')
