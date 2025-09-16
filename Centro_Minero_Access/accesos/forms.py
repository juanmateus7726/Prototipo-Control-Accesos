from django import forms 
from .models import Acceso
from usuarios.models import  Usuario

class AccesoForm(forms.ModelForm):
    # Cambiar a ModelChoiceField para seleccionar usuario
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(activo=True),
        empty_label="Seleccione un usuario",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'usuario-select'
        })
    )
    
    # Definir opciones para laboratorio
    LABORATORIO_CHOICES = [
        ('sistemas', '💻 Laboratorio de Sistemas'),
        ('quimica', '🧪 Laboratorio de Química Aplicada'),
        ('carbones', '⚫ Laboratorio de Carbones'),
        ('biotecnologia', '🧬 Laboratorio de Biotecnología'),
        ('beneficios', '⛏️ Lab. Beneficios Minerales'),
        ('aguas', '💧 Laboratorio de Aguas'),
        ('suelos', '🌱 Laboratorio de Suelos'),
        ('abc_maquinaria', '🚜 Ambiente ABC - Maquinaria Pesada'),
        ('bilinguismo', '🗣️ Ambiente de Bilingüismo'),
        ('minas_didacticas', '⛏️ Minas Didácticas'),
    ]
    
    laboratorio = forms.ChoiceField(
        choices=LABORATORIO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'laboratorio-select'
        })
    )
    
    # Definir opciones para método
    METODO_CHOICES = [
        ('carnet_manual', '🎫 Carnet Manual'),
        ('reconocimiento_facial', '📷 Reconocimiento Facial'),
        ('tarjeta_rfid', '🔷 Tarjeta RFID'),
        ('huella_digital', '📱 Huella Digital'),
    ]
    
    metodo = forms.ChoiceField(
        choices=METODO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'metodo-select'
        })
    )

    class Meta:
        model = Acceso
        fields = ['usuario', 'laboratorio', 'metodo']