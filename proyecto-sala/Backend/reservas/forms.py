from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    # Declaramos las contraseñas explícitamente para evitar errores de herencia
    password1 = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    password2 = forms.CharField(
        label="Confirmación de contraseña", 
        widget=forms.PasswordInput, 
        help_text="Ingresa la misma contraseña para verificar."
    )

    class Meta:
        model = Usuario
        # AQUÍ ESTÁ LA LISTA COMPLETA DE TUS DATOS IMPORTANTES
        fields = (
            'username', 
            'email', 
            'nombres', 
            'apellido_paterno', 
            'apellido_materno', # Faltaba este
            'matricula_ud', 
            'division', 
            'telefono'          # Y este es el que mencionabas
        )
    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            print("\n========================================")
            print(" ERRORES ENCONTRADOS:", self.errors)
            print("========================================\n")
        return cleaned_data    

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = '__all__'