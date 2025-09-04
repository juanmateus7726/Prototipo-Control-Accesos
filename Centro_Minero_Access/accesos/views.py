from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'accesos/index.html')


def historial(request):
    return render(request, 'accesos/historial.html')

def detector_view(request):
    return render(request, 'accesos/detector.html')