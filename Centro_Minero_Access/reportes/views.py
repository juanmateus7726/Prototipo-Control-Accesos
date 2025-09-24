
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from accesos.models import Acceso

def reporte_accesos_pdf(request):
	# Filtros básicos (puedes expandir esto según tus necesidades)
	accesos = Acceso.objects.all().order_by('-fecha_hora')[:100]
	template_path = 'reportes/reporte_pdf.html'
	context = {'accesos': accesos}
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="reporte_accesos.pdf"'
	template = get_template(template_path)
	html = template.render(context)
	pisa_status = pisa.CreatePDF(html, dest=response)
	if pisa_status.err:
		return HttpResponse('Error al generar el PDF', status=500)
	return response