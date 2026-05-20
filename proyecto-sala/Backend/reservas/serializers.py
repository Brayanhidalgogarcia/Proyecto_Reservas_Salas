from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (Division, Asignatura, Sala, Maestro, 
                     Reserva, 
                     Usuario,Reporte,Actividad)
from django.utils import timezone



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
       
        data = super().validate(attrs)
        
        
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['is_superuser'] = self.user.is_superuser
        
        try:
            
            maestro = self.user.perfil_maestro
            
            
            if maestro:
                data['nombre_completo'] = f"{maestro.nombre} {maestro.apellido_p}"
                
                data['division'] = maestro.division.nombre_division if maestro.division else None
            
        except Exception:

            data['nombre_completo'] = self.user.username 
            data['division'] = None

        return data
class UsuarioSerializer(serializers.ModelSerializer):
    division_nombre = serializers.ReadOnlyField(source='division.nombre_division')

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nombres', 'apellido_paterno', 'apellido_materno', 'matricula_ud', 'telefono', 'division', 'division_nombre']


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'


class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['division'] = str(instance.division) 
        return response


class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['division'] = str(instance.division) 
        return response
    
class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ['id', 'nombre_actividad', 'activo']


class MaestroSerializer(serializers.ModelSerializer):
  
    usuario_id = serializers.ReadOnlyField(source='usuario.id')

    class Meta:
        model = Maestro
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['division'] = str(instance.division) 
        return response


class ReservaSerializer(serializers.ModelSerializer):
    division = serializers.StringRelatedField(source='sala.division', read_only=True)
    creado_por_id = serializers.ReadOnlyField(source='creado_por.id')

    class Meta:
        model = Reserva
        
        fields = [
            'id', 'actividad', 'maestro', 'asignatura', 'sala', 
            'division', 'tema', 'requerimientos', 'inicio', 'fin', 
            'fecha_apartado', 'creado_por_id'
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        
        
        response['actividad'] = str(instance.actividad) if instance.actividad else None
        response['maestro'] = str(instance.maestro) if instance.maestro else None
        response['asignatura'] = str(instance.asignatura) if instance.asignatura else None
        response['sala'] = str(instance.sala) if instance.sala else None
        
        return response

    def validate(self, data):
       
        actividad = data.get('actividad')
        asignatura = data.get('asignatura')

        if actividad:
           
            if actividad.nombre_actividad == 'Asignatura':
                if not asignatura:
                    
                    raise serializers.ValidationError({
                        "asignatura": "Es obligatorio seleccionar una asignatura para este tipo de actividad."
                    })
            else:
                
                data['asignatura'] = None

     
        sala = data.get('sala')
        inicio = data.get('inicio')
        fin = data.get('fin')

        if inicio >= fin:
            raise serializers.ValidationError({
                "detail": "La hora de inicio debe ser anterior a la hora de fin."
            })

        if timezone.is_naive(inicio):
            inicio = timezone.make_aware(inicio)
        if timezone.is_naive(fin):
            fin = timezone.make_aware(fin)
            
        inicio_local = timezone.localtime(inicio)
        fin_local = timezone.localtime(fin)
        
        hora_inicio = inicio_local.hour
        hora_fin = fin_local.hour
        minuto_fin = fin_local.minute

        if hora_inicio < 8 or (hora_fin > 16) or (hora_fin == 16 and minuto_fin > 0):
             raise serializers.ValidationError({
                "detail": "El horario de servicio es exclusivamente de 08:00 a 16:00."
            })

       
        qs = Reserva.objects.filter(
            sala=sala,
            inicio__lt=fin,
            fin__gt=inicio
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            conflicto = qs.first()
            inicio_mx = timezone.localtime(conflicto.inicio)
            fin_mx = timezone.localtime(conflicto.fin)
            h_ini = inicio_mx.strftime('%H:%M')
            h_fin = fin_mx.strftime('%H:%M')
            
            raise serializers.ValidationError({
                "detail": f"Conflicto: La sala ya está ocupada por {conflicto.maestro} de {h_ini} a {h_fin}."
            })

        return data

class ReporteSerializer(serializers.ModelSerializer):
    
    tipo_legible = serializers.CharField(source='get_tipo_display', read_only=True)
    
    
    division_nombre = serializers.ReadOnlyField(source='division.NombreDivision')
    
  
    creado_por = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Reporte
        fields = [
            'id', 
            'titulo', 
            'archivo', 
            'fecha_generacion', 
            'tipo', 
            'tipo_legible',       
            'fecha_inicio_datos', 
            'fecha_fin_datos',
            'usuario',           
            'creado_por',         
            'division',           
            'division_nombre'     
        ]
        
        
        read_only_fields = ['usuario', 'division', 'fecha_generacion']
        



class RegistroMaestroSerializer(serializers.ModelSerializer):
    
    matricula = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        
        fields = ['username', 'email', 'password', 'matricula']

    def validate_matricula(self, value):
        """
        Valida que el maestro exista y no tenga usuario ya asignado.
        """
        try:
            maestro = Maestro.objects.get(matricula_m=value)
        except Maestro.DoesNotExist:
            raise serializers.ValidationError("Error: No existe ningún maestro registrado con esta matrícula.")

        if maestro.usuario is not None:
            raise serializers.ValidationError(f"Error: El maestro {maestro.nombre} {maestro.apellido_p} ya tiene un usuario activo.")
        
        return value

    def create(self, validated_data):
      
        matricula = validated_data.pop('matricula')
        password = validated_data.pop('password')
        
     
        user = Usuario.objects.create_user(
            password=password,
            **validated_data 
        )

      
        maestro = Maestro.objects.get(matricula_m=matricula)
        maestro.usuario = user
        maestro.save()

        return user