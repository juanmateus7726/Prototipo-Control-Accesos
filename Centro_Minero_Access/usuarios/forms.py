from django  import forms, froms 
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['carnet', 'nombre', 'tipo', 'activo']
        