# forms.py - ACTUALIZADO
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para registrar nuevos usuarios.
    Incluye email obligatorio y campos estilizados para el template.
    """
    email = forms.EmailField(
        required=True,
        help_text='Requerido: se usará para comunicación y recuperación de cuenta.',
        widget=forms.EmailInput(attrs={
            'placeholder': 'correo@ejemplo.com',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Nombre de usuario',
                'class': 'form-control'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Contraseña',
                'class': 'form-control'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirmar contraseña',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'username': 'Requerido. Solo letras, números y @/./+/-/_',
            'password1': 'La contraseña debe tener al menos 8 caracteres.',
            'password2': 'Introduce la misma contraseña nuevamente.',
        }

    def save(self, commit=True):
        """
        Guarda el usuario con el email agregado.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
