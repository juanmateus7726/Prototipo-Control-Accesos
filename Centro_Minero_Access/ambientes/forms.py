# ambientes/forms.py
from django import forms
from .models import Ambiente

class AmbienteForm(forms.ModelForm):
    class Meta:
        model = Ambiente
        fields = ['nombre', 'codigo', 'estado', 'capacidad', 'riesgo']