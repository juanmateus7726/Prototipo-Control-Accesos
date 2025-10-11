"""
Backend de email personalizado para resolver problemas de SSL
en Python 3.13+ en Windows.
"""
import ssl
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend


class CustomEmailBackend(DjangoEmailBackend):
    """
    Backend SMTP personalizado que usa contexto SSL sin verificación.
    Soluciona el error: certificate verify failed
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crear contexto SSL que no verifica certificados
        self.ssl_context = ssl._create_unverified_context()