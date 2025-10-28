# account/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label="Teléfono", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    CIUDADES_COLOMBIA = [
        ('bogota', 'Bogotá'),
        ('medellin', 'Medellín'),
        ('cali', 'Cali'),
        ('barranquilla', 'Barranquilla'),
        ('cartagena', 'Cartagena'),
        ('cucuta', 'Cúcuta'),
        ('bucaramanga', 'Bucaramanga'),
        ('pereira', 'Pereira'),
        ('santamarta', 'Santa Marta'),
        ('manizales', 'Manizales'),
        ('ibague', 'Ibagué'),
        ('neiva', 'Neiva'),
        ('villavicencio', 'Villavicencio'),
        ('pasto', 'Pasto'),
        ('monteria', 'Montería'),
        ('popayan', 'Popayán'),
        ('sincelejo', 'Sincelejo'),
        ('valledupar', 'Valledupar'),
        ('armenia', 'Armenia'),
        ('riohacha', 'Riohacha'),
    ]

    ciudad_residencia = forms.ChoiceField(
        label="Ciudad de residencia",
        choices=CIUDADES_COLOMBIA,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # Más adelante guardaremos teléfono y ciudad en Perfil
        if commit:
            user.save()
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded'}),
        }
        
        
class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    username = forms.CharField(label="Nombre de usuario", required=True)

    class Meta:
        model = Profile
        fields = ['telefono', 'ciudad']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded'}),
            'ciudad': forms.Select(attrs={'class': 'form-select rounded'}),
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username

    def save(self, user, commit=True):
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            super().save(commit)
        return user
