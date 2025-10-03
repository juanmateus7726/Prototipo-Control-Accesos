from django import forms
from .models import Usuario, Registro
from ambientes.models import Ambiente

class UsuarioForm(forms.ModelForm):
    # NUEVO: Checklist de ambientes (ManyToMany)
    ambientes_directos = forms.ModelMultipleChoiceField(
        queryset=Ambiente.objects.all().order_by('nombre'),  # Todos los ambientes, ordenados
        required=False,  # Opcional: Puede no seleccionar ninguno
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        }),
        label="Ambientes Permitidos",
        help_text="Seleccione los ambientes a los que este usuario tiene acceso. Mantenga presionado Ctrl para seleccionar múltiples."
    )


    class Meta:
        model = Usuario
        fields = ['tipo_identificacion', 
                'numero_identificacion',
                'nombre',
                'tipo',
                'activo',
                'ambientes_directos']
        widgets = {
            'tipo_identificacion': forms.Select(attrs={
                'class': 'form-control',
            }),
            'numero_identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1000000000',
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