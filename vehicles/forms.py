from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'marca', 'modelo', 'anio', 'descripcion', 'precio',
            'ubicacion', 'kilometraje', 'motor'
        ]
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corolla'}),
            'anio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2019'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del vehículo...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 55000000'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Medellín'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 45000'}),
            'motor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1.6L'}),
        }
    