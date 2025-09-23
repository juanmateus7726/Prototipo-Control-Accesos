from django import forms
from .models import Usuario, Registro

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['carnet', 'nombre', 'tipo', 'activo']
        widgets = {
            'carnet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del usuario'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class RegistroAccesoForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['usuario', 'tipo', 'metodo', 'ambiente']
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'metodo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ambiente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del ambiente'
            })
        }