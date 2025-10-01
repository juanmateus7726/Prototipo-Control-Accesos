from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from accesos.models import Acceso
from django.conf import settings
import base64
import os
from io import BytesIO
from datetime import datetime

def reporte_accesos_pdf(request):
    """
    Genera un reporte PDF de los accesos registrados en el sistema.
    """
    # Obtener parámetros de filtrado opcionales (puedes expandir esto)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)
    usuario_id = request.GET.get('usuario', None)
    ambiente_id = request.GET.get('ambiente', None)
    
    # Query base
    accesos = Acceso.objects.all()
    
    # Aplicar filtros si existen
    if fecha_inicio:
        accesos = accesos.filter(fecha_hora__gte=fecha_inicio)
    if fecha_fin:
        accesos = accesos.filter(fecha_hora__lte=fecha_fin)
    if usuario_id:
        accesos = accesos.filter(usuario_id=usuario_id)
    if ambiente_id:
        accesos = accesos.filter(ambiente_id=ambiente_id)
    
    # Ordenar y limitar resultados
    accesos = accesos.select_related('usuario', 'ambiente').order_by('-fecha_hora')[:100]
    
    # Leer y convertir el logo a base64
    # Intenta diferentes extensiones de imagen
    logo_extensions = ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']
    logo_base64 = ''
    
    for ext in logo_extensions:
        logo_path = os.path.join(settings.MEDIA_ROOT, 'reportes', 'imagenes', f'logo.{ext}')
        if os.path.exists(logo_path):
            try:
                with open(logo_path, 'rb') as image_file:
                    logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                print(f"✓ Logo cargado correctamente desde: {logo_path}")
                break
            except Exception as e:
                print(f"⚠️ Error al cargar el logo: {str(e)}")
        else:
            continue
    
    if not logo_base64:
        print(f"⚠️ No se encontró ningún logo en: {settings.MEDIA_ROOT}/reportes/imagenes/")
    
    # Preparar contexto para el template
    template_path = 'reportes/reporte_pdf.html'
    context = {
        'accesos': accesos,
        'logo_base64': logo_base64,
        'total_accesos': accesos.count(),
        'fecha_generacion': datetime.now(),
    }
    
    # Crear respuesta HTTP con PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nombre del archivo con timestamp
    filename = f'reporte_accesos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Renderizar template
    template = get_template(template_path)
    html = template.render(context)
    
    # Crear PDF con xhtml2pdf
    pisa_status = pisa.CreatePDF(
        src=html.encode('utf-8'),
        dest=response,
        encoding='utf-8'
    )
    
    # Verificar si hubo errores
    if pisa_status.err:
        error_msg = f'Error al generar el PDF. Código de error: {pisa_status.err}'
        print(f"❌ {error_msg}")
        return HttpResponse(error_msg, status=500)
    
    return response


def vista_previa_reporte(request):
    """
    Vista opcional para previsualizar el reporte en HTML antes de generar el PDF.
    Útil para debugging y ajustes de diseño.
    """
    accesos = Acceso.objects.select_related('usuario', 'ambiente').order_by('-fecha_hora')[:100]
    
    logo_path = os.path.join(settings.MEDIA_ROOT, 'reportes', 'imagenes', 'logo.jpg')
    logo_base64 = ''
    
    try:
        with open(logo_path, 'rb') as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        pass
    
    context = {
        'accesos': accesos,
        'logo_base64': logo_base64,
        'total_accesos': accesos.count(),
        'fecha_generacion': datetime.now(),
    }
    
    return render(request, 'reportes/reporte_pdf.html', context)