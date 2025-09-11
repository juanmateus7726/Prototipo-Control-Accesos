from django import forms
from .models import Ambiente

class AmbienteForm(forms.ModelForm):
    class Meta:
        model = Ambiente
        fields = ['nombre', 'protocolo', 'riesgo']
        widgets = {
            'protocolo': forms.Textarea(attrs={'rows': 4}),
        }