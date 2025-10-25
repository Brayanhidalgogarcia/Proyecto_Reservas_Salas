from django.db import models

from django.contrib.auth.models import User


class PerfilAdministrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricula_ud = models.CharField(max_length=20, primary_key=True, db_column='MatriculaUD')
    telefono = models.IntegerField(null=True, blank=True, db_column='Telefono')
    division = models.ForeignKey('Division', on_delete=models.SET_NULL, null=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'administradorsalas' 

    def __str__(self):
        return self.user.username


class Division(models.Model):
    clave_division = models.CharField(
        max_length=20, primary_key=True, db_column='ClaveDivision')
    nombre_division = models.CharField(
        max_length=80, null=True, blank=True, db_column='NombreDivision')

    class Meta:
        db_table = 'division'

    def __str__(self):
     
        if self.nombre_division:
            return self.nombre_division
        return self.clave_division


class Asignatura(models.Model):
    clave_asignatura = models.CharField(
        max_length=20, primary_key=True, db_column='ClaveAsignatura')
    nombre_asignatura = models.CharField(
        max_length=80, null=True, blank=True, db_column='NombreAsignatura')
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'asignatura'

    def __str__(self):
        if self.nombre_asignatura:
            return self.nombre_asignatura
        return self.clave_asignatura


class Sala(models.Model):
    clave_sala = models.CharField(
        max_length=20, primary_key=True, db_column='ClaveSala')
    nombre_sala = models.CharField(
        max_length=80, null=True, blank=True, db_column='NombreSala')
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'sala'

    def __str__(self):
       
        if self.nombre_sala:
            return self.nombre_sala
        return self.clave_sala


class Maestro(models.Model):
    matricula_m = models.CharField(
        max_length=20, primary_key=True, db_column='MatriculaM')
    nombre = models.CharField(max_length=40, null=True,
                              blank=True, db_column='Nombre')
    apellido_p = models.CharField(
        max_length=84, null=True, blank=True, db_column='ApellidoP')
    apellido_m = models.CharField(
        max_length=84, null=True, blank=True, db_column='ApellidoM')
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, db_column='ClaveDivision')

    class Meta:
        db_table = 'maestro'

    def __str__(self):
       
        parts = [self.nombre, self.apellido_p]
        full_name = " ".join(part for part in parts if part)
        if full_name:
            return full_name
        return self.matricula_m


class Reserva(models.Model):
   
    maestro = models.ForeignKey(
        Maestro, on_delete=models.CASCADE, null=True, db_column='MatriculaM')
    asignatura = models.ForeignKey(
        Asignatura, on_delete=models.CASCADE, null=True, db_column='ClaveAsignatura')
    sala = models.ForeignKey(
        Sala, on_delete=models.CASCADE, null=True, db_column='ClaveSala')
    tema = models.CharField(max_length=80, null=True,
                            blank=True, db_column='Tema')

   
    inicio = models.DateTimeField()

 
    fin = models.DateTimeField()

  
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reserva'

    def __str__(self):
       
        sala_info = str(self.sala) if self.sala else "Sala Desconocida"
        maestro_info = str(
            self.maestro) if self.maestro else "Maestro Desconocido"

        if self.inicio:
           
            fecha_formateada = self.inicio.strftime('%d/%m/%Y a las %H:%M')
            return f"Reserva en {sala_info} por {maestro_info} el {fecha_formateada}"
        else:
            
            return f"Reserva en {sala_info} por {maestro_info} (fecha pendiente)"
