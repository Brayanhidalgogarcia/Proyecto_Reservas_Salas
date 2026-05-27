from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Division, Asignatura, Sala, Maestro, Reserva, Reporte, Actividad, Edificio
from .forms import UsuarioCreationForm, UsuarioChangeForm

admin.site.site_header = "Administración de Salas UJAT"

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    
    list_display = [
        'username', 
        'email', 
        'is_staff', 
        'maestro_vinculado'
    ]
    
    search_fields = ['username', 'email']
    list_filter = ['is_staff', 'is_superuser', 'is_active']

    
    def maestro_vinculado(self, obj):
        if hasattr(obj, 'perfil_maestro') and obj.perfil_maestro:
            return f"{obj.perfil_maestro.nombre} {obj.perfil_maestro.apellido_p} ({obj.perfil_maestro.matricula_m})"
        return "--- Sin Vincular ---"
    
    maestro_vinculado.short_description = 'Docente Asignado'

 
    fieldsets = (
        ('Cuenta', {'fields': ('username', 'password')}),
        ('Información de Contacto', {
            'fields': ('email',) 
        }),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    
   
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'matricula',
                'username', 
                'email', 
                'password1',  
                'password2'
            ),
        }),
    )


@admin.register(Maestro)
class MaestroAdmin(admin.ModelAdmin):
    list_display = [
        'matricula_m', 
        'nombre_completo', 
        'division', 
        'telefono', 
        'usuario_asociado'
    ]
    
    search_fields = ['matricula_m', 'nombre', 'apellido_p']
    list_filter = ['division']
    
    fields = (
        ('matricula_m', 
        'nombre', 
        'apellido_p', 
        'apellido_m',
        'telefono',
        'division',
        'usuario') 
    )

    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido_p} {obj.apellido_m or ''}"
    
    def usuario_asociado(self, obj):
        return obj.usuario.username if obj.usuario else "Sin Usuario"
    


admin.site.register(Division)
admin.site.register(Asignatura)
admin.site.register(Edificio)
admin.site.register(Sala)
admin.site.register(Reserva)
admin.site.register(Reporte)
admin.site.register(Actividad) 