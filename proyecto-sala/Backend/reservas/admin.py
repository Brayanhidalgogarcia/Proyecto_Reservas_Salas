from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Division, Asignatura, Sala, Maestro, Reserva, Reporte
from .forms import UsuarioCreationForm, UsuarioChangeForm

admin.site.site_header = "Administración de Salas UJAT"

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    
    # 1. QUÉ COLUMNAS VER EN LA LISTA (Tabla principal)
    list_display = [
        'username', 
        'nombres', 
        'apellido_paterno', 
        'matricula_ud', 
        'division', 
        'telefono',   # Agregado para verlo rápido en la lista
        'is_staff'
    ]
    
    search_fields = ['username', 'email', 'nombres', 'apellido_paterno', 'matricula_ud']
    list_filter = ['division', 'is_staff', 'groups']

    # 2. QUÉ CAMPOS VER AL EDITAR UN USUARIO EXISTENTE
    fieldsets = (
        ('Cuenta', {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': (
                'nombres', 
                'apellido_paterno', 
                'apellido_materno', # Agregado
                'email', 
                'telefono'          # Agregado
            )
        }),
        ('Información Académica', {
            'fields': ('matricula_ud', 'division')
        }),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 3. QUÉ CAMPOS VER AL CREAR (AGREGAR) UN USUARIO NUEVO
    # Esta es la parte crítica que fallaba antes. Aquí están TODOS tus campos.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'nombres', 
                'apellido_paterno', 
                'apellido_materno', # Agregado
                'matricula_ud', 
                'division', 
                'telefono',         # IMPORTANTE: Aquí se pide el teléfono al registrar
                'password1', 
                'password2'
            ),
        }),
    )

# --- REGISTRO DEL RESTO DE MODELOS ---
admin.site.register(Division)
admin.site.register(Asignatura)
admin.site.register(Sala)
admin.site.register(Maestro)
admin.site.register(Reserva)
admin.site.register(Reporte)