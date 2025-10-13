from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
import os
from django.conf import settings

@login_required
def pagina_ayuda(request):
    """
    Página de ayuda con información y enlaces a recursos
    """
    return render(request, 'ayuda/index.html')

@login_required
def descargar_manual(request):
    """
    Sirve el archivo PDF del manual de usuario para descarga
    """
    # Ruta al archivo PDF
    pdf_path = os.path.join(settings.BASE_DIR, 'ayuda', 'static', 'ayuda', 'pdfs', 'manual_usuario.pdf')
    
    # Verificar si el archivo existe
    if not os.path.exists(pdf_path):
        raise Http404("El manual de usuario no está disponible en este momento. Verifica que el archivo PDF esté en: ayuda/static/ayuda/pdfs/manual_usuario.pdf")
    
    try:
        # Abrir el archivo PDF
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        
        # Para que se abra en el navegador
        response['Content-Disposition'] = 'inline; filename="Manual_Usuario_SENA.pdf"'
        
        return response
    except Exception as e:
        raise Http404(f"Error al cargar el manual: {str(e)}")