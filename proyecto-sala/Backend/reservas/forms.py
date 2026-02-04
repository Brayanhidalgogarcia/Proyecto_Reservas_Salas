from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario,Maestro
from django.core.exceptions import ValidationError


class UsuarioCreationForm(UserCreationForm):
    # Mantenemos tus campos explícitos de contraseña
    matricula = forms.CharField(
        label="Matrícula del Docente",
        max_length=20,
        help_text="Ingresa la matrícula del maestro para vincularlo a este usuario."
    )
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
        
        fields = (
            'username', 
            'email', 
        )
        
        
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        try:
            maestro = Maestro.objects.get(matricula_m=matricula)
        except Maestro.DoesNotExist:
            raise ValidationError("No existe ningún maestro con esta matrícula.")
        
        if maestro.usuario is not None:
            raise ValidationError(f"El maestro {maestro.nombre} ya tiene un usuario asignado ({maestro.usuario.username}).")
        
        return matricula
        

    def clean(self):
        # Tu lógica de depuración se queda, es útil.
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("password1")
        pass2 = cleaned_data.get("password2")
        
        if pass1 and pass2 and pass1 != pass2:
            self.add_error("password2", "Las contraseñas no coinciden")

        if self.errors:
            print("\n========================================")
            print(" ERRORES ENCONTRADOS:", self.errors)
            print("========================================\n")
        return cleaned_data    

    def save(self, commit=True):
        # Primero guardamos al usuario (Auth)
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
            # AQUÍ ESTÁ LA LÓGICA QUE FALTABA:
            # Buscamos al maestro por la matrícula que escribiste y le asignamos el usuario
            matricula = self.cleaned_data['matricula']
            maestro = Maestro.objects.get(matricula_m=matricula)
            maestro.usuario = user
            maestro.save()
            
        return user
    
class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        # Limitamos los campos para evitar errores si Django intenta buscar columnas viejas
        fields = ('username', 'email')