from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. MODELOS DE CATÁLOGOS (Sin cambios, necesarios para las llaves foráneas)

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
    # Opcional: Capacidad para calcular aforo
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

    class Meta:
        db_table = 'maestro'

    def __str__(self):
        return f"{self.nombre} {self.apellido_p}"



class Usuario(AbstractUser):
    # Desactivamos los nombres por defecto de Django para usar los atomizados latinos
    first_name = None
    last_name = None

    # Campos Personalizados
    email = models.EmailField(unique=True, db_column='Email') # Email obligatorio y único
    matricula_ud = models.CharField(max_length=20, null=True, blank=True, db_column='MatriculaUD')
    
    # Nombre Atomizado
    nombres = models.CharField(max_length=40, null=True, blank=True, db_column='Nombres')
    apellido_paterno = models.CharField(max_length=40, null=True, blank=True, db_column='ApellidoPaterno')
    apellido_materno = models.CharField(max_length=40, null=True, blank=True, db_column='ApellidoMaterno')
    
    telefono = models.CharField(max_length=20, null=True, blank=True, db_column='Telefono')
    
    # Relación con División (Para saber qué administrador pertenece a qué área)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'usuario_sistema' # Tabla nueva limpia

    def __str__(self):
        # Muestra "Juan Perez (admin)"
        return f"{self.nombres} {self.apellido_paterno} ({self.username})"

# 3. MODELO DE RESERVAS (Intacto)

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

# 4. NUEVO MODELO: REPORTES (Historial de Archivos)

class Reporte(models.Model):
    # Opciones para categorizar el reporte
    class TipoReporte(models.TextChoices):
        OCUPACION_SALAS = 'OCUPACION', 'Ocupación por Sala'
        ACTIVIDAD_DOCENTE = 'DOCENTE', 'Actividad por Maestro'
        GENERAL_MENSUAL = 'GENERAL', 'Resumen General Mensual'

    # --- DATOS BÁSICOS ---
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='reportes_generados/', null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    
    # Relación con el usuario (Admin) que lo generó
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)

    # --- FACTOR DE ESCALABILIDAD (El cambio clave) ---
    # Vinculamos el reporte a una División.
    # AUNQUE AHORA SOLO SEA DACITY, este campo es el que permite la expansión futura.
    # Cuando filtres reportes, siempre harás: Reporte.objects.filter(division=usuario.division)
    division = models.ForeignKey('Division', on_delete=models.CASCADE)

    # --- METADATOS PARA FILTRADO (BI) ---
    tipo = models.CharField(
        max_length=20, 
        choices=TipoReporte.choices, 
        default=TipoReporte.GENERAL_MENSUAL
    )

    # Rango de fechas que abarca la información del reporte
    fecha_inicio_datos = models.DateField(null=True, blank=True)
    fecha_fin_datos = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'reporte_historial'
        ordering = ['-fecha_generacion'] 

    def __str__(self):
        # Muestra: "Reporte Enero (Dacity) - Ocupación"
        div_nombre = self.division.nombre_division if self.division else "Sin División"
        return f"{self.titulo} ({div_nombre}) - {self.get_tipo_display()}"