from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from accesos.models import Acceso
from django.conf import settings
import base64
import os

def reporte_accesos_pdf(request):
    # Filtros básicos (puedes expandir esto según tus necesidades)
    accesos = Acceso.objects.all().order_by('-fecha_hora')[:100]
    
    # Leer y convertir el logo a base64
    logo_path = os.path.join(settings.MEDIA_ROOT, 'reportes','imagenes', 'logo.jpg')
    
    try:
        with open(logo_path, 'rb') as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        # Si no encuentra el logo, usa una cadena vacía
        logo_base64 = ''
    
    template_path = 'reportes/reporte_pdf.html'
    context = {
        'accesos': accesos,
        'logo_base64': logo_base64
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_accesos.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    
    return response