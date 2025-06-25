from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, PartidaArancelaria

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', required=True)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if '  ' in username:
            raise forms.ValidationError("El nombre de usuario no puede contener espacios dobles.")
        if username.strip() != username:
            raise forms.ValidationError("El nombre de usuario no debe comenzar ni terminar con espacios.")
        return username
    
class CargarExcelForm(forms.Form):
    archivo = forms.FileField(label="Archivo Excel (.xlsx)")

class PartidaForm(forms.ModelForm):
    class Meta:
        model = PartidaArancelaria
        fields = '__all__'
