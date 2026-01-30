import os
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models.signals import post_delete
from django.dispatch import receiver

# 1. MODELOS DE CATÁLOGOS

class Division(models.Model):
    clave_division = models.CharField(max_length=20, primary_key=True, db_column='ClaveDivision')
    nombre_division = models.CharField(max_length=80, null=True, blank=True, db_column='NombreDivision')

    class Meta:
        db_table = 'division'

    def __str__(self):
        return self.nombre_division or self.clave_division

class Asignatura(models.Model):
    clave_asignatura = models.CharField(max_length=20, primary_key=True, db_column='ClaveAsignatura')
    nombre_asignatura = models.CharField(max_length=80, null=True, blank=True, db_column='NombreAsignatura')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'asignatura'

    def __str__(self):
        return self.nombre_asignatura or self.clave_asignatura

class Sala(models.Model):
    clave_sala = models.CharField(max_length=20, primary_key=True, db_column='ClaveSala')
    nombre_sala = models.CharField(max_length=80, null=True, blank=True, db_column='NombreSala')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, db_column='ClaveDivision')
    capacidad = models.IntegerField(null=True, blank=True, db_column='Capacidad')

    class Meta:
        db_table = 'sala'

    def __str__(self):
        return self.nombre_sala or self.clave_sala

class Maestro(models.Model):
    matricula_m = models.CharField(max_length=20, primary_key=True, db_column='MatriculaM')
    nombre = models.CharField(max_length=40, null=True, blank=True, db_column='Nombre')
    apellido_p = models.CharField(max_length=84, null=True, blank=True, db_column='ApellidoP')
    apellido_m = models.CharField(max_length=84, null=True, blank=True, db_column='ApellidoM')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, db_column='ClaveDivision')

    # --- NUEVO CAMPO: VINCULACIÓN CON USUARIO ---
    # Usamos 'Usuario' entre comillas porque el modelo Usuario se define más abajo.
    usuario = models.OneToOneField(
        'Usuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='perfil_maestro',
        db_column='Usuario_ID'
    )

    class Meta:
        db_table = 'maestro'

    def __str__(self):
        return f"{self.nombre} {self.apellido_p}"


# 2. MODELO DE USUARIO PERSONALIZADO

class Usuario(AbstractUser):
    # Desactivamos los nombres por defecto de Django
    first_name = None
    last_name = None

    # Campos Personalizados
    email = models.EmailField(unique=True, db_column='Email')
    matricula_ud = models.CharField(max_length=20, null=True, blank=True, db_column='MatriculaUD')
    
    # Nombre Atomizado
    nombres = models.CharField(max_length=40, null=True, blank=True, db_column='Nombres')
    apellido_paterno = models.CharField(max_length=40, null=True, blank=True, db_column='ApellidoPaterno')
    apellido_materno = models.CharField(max_length=40, null=True, blank=True, db_column='ApellidoMaterno')
    
    telefono = models.CharField(max_length=20, null=True, blank=True, db_column='Telefono')
    
    # Relación con División
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'usuario_sistema'

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} ({self.username})"

# 3. MODELO DE RESERVAS

class Reserva(models.Model):
    maestro = models.ForeignKey(Maestro, on_delete=models.CASCADE, null=True, blank=True, db_column='MatriculaM')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, null=True, blank=True, db_column='ClaveAsignatura')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, null=True, blank=True, db_column='ClaveSala')
    tema = models.CharField(max_length=80, null=True, blank=True, db_column='Tema')

    inicio = models.DateTimeField(db_column='FechaHoraInicio') 
    fin = models.DateTimeField(db_column='FechaHoraFin') 
    
    fecha_apartado = models.DateTimeField(auto_now_add=True)
    
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_creadas')

    class Meta:
        db_table = 'reserva'

    def __str__(self):
        sala_info = str(self.sala) if self.sala else "Sala Desconocida"
        if self.inicio:
            return f"Reserva en {sala_info} el {self.inicio.strftime('%d/%m/%Y a las %H:%M')}"
        return f"Reserva en {sala_info}"

# 4. MODELO DE REPORTES

class Reporte(models.Model):
    class TipoReporte(models.TextChoices):
        OCUPACION_SALAS = 'OCUPACION', 'Ocupación por Sala'
        ACTIVIDAD_DOCENTE = 'DOCENTE', 'Actividad por Maestro'
        GENERAL_MENSUAL = 'GENERAL', 'Resumen General Mensual'

    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='reportes_generados/', null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)
    division = models.ForeignKey('Division', on_delete=models.CASCADE)

    tipo = models.CharField(
        max_length=20, 
        choices=TipoReporte.choices, 
        default=TipoReporte.GENERAL_MENSUAL
    )

    fecha_inicio_datos = models.DateField(null=True, blank=True)
    fecha_fin_datos = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'reporte_historial'
        ordering = ['-fecha_generacion'] 

    def __str__(self):
        div_nombre = self.division.nombre_division if self.division else "Sin División"
        return f"{self.titulo} ({div_nombre}) - {self.get_tipo_display()}"
    
@receiver(post_delete, sender=Reporte)
def eliminar_archivo_reporte(sender, instance, **kwargs):
    """
    Borra el archivo físico cuando se elimina el registro de Reporte en la BD.
    """
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)