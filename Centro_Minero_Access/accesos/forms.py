from django import forms
from .models import Acceso

class AccesoForm(forms.ModelForm):
    class Meta:
        model = Acceso
        fields = ['usuario', 'laboratorio', 'metodo']
        widgets = {
            'usuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o ID del usuario'}),
            'laboratorio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Laboratorio'}),
            'metodo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: carnet_manual'}),
        }