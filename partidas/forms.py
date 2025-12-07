from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, PartidaArancelaria, Rol

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


class UsuarioAdminForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput, required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'is_active']

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(p1) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password1')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user
