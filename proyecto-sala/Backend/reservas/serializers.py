from rest_framework import serializers
# Importamos el serializador base de JWT para extenderlo
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (Division, Asignatura, Sala, Maestro, 
                     Reserva, 
                     Usuario,Reporte)
from django.contrib.auth.models import User
from django.utils import timezone


# --- PASO 1.1: IDENTIDAD EN EL LOGIN ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 1. Obtenemos los tokens básicos (access y refresh)
        data = super().validate(attrs)
        
        # 2. Datos básicos de la cuenta
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['is_superuser'] = self.user.is_superuser
        
        # 3. RECUPERACIÓN INTELIGENTE DE DATOS (NUEVA LÓGICA)
        # Intentamos buscar si este usuario tiene un maestro vinculado
        try:
            # Accedemos a la relación inversa definida en models.py (related_name='perfil_maestro')
            maestro = self.user.perfil_maestro
            
            # Si existe el maestro, sacamos sus datos reales
            if maestro:
                data['nombre_completo'] = f"{maestro.nombre} {maestro.apellido_p}"
                # Validamos que tenga división asignada antes de acceder a su nombre
                data['division'] = maestro.division.nombre_division if maestro.division else None
            
        except Exception:
            # CASO ADMIN PURO O USUARIO SIN VINCULAR:
            # Si entra aquí es porque self.user.perfil_maestro no existe.
            # Devolvemos valores neutros para que el frontend no falle.
            data['nombre_completo'] = self.user.username # Usamos el usuario como nombre
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


class MaestroSerializer(serializers.ModelSerializer):
  
    usuario_id = serializers.ReadOnlyField(source='usuario.id')

    class Meta:
        model = Maestro
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['division'] = str(instance.division) 
        return response


# --- PASO 1.2: PROPIEDAD DE LA RESERVA ---
class ReservaSerializer(serializers.ModelSerializer):
    division = serializers.StringRelatedField(source='sala.division', read_only=True)
    
    
    creado_por_id = serializers.ReadOnlyField(source='creado_por.id')

    class Meta:
        model = Reserva
        fields = ['id', 'maestro', 'asignatura', 'sala', 'division', 'tema', 'inicio', 'fin', 'fecha_apartado', 'creado_por_id']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['maestro'] = str(instance.maestro)
        response['asignatura'] = str(instance.asignatura)
        response['sala'] = str(instance.sala)
        return response

    def validate(self, data):
        
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
    # --- SERIALIZER DE REPORTES ---
class ReporteSerializer(serializers.ModelSerializer):
    # Metadatos extra para facilitar la vida al Frontend
    # Muestra "Ocupación por Sala" en lugar de "OCUPACION"
    tipo_legible = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # Muestra el nombre de la división en lugar de solo el ID (Clave)
    division_nombre = serializers.ReadOnlyField(source='division.NombreDivision')
    
    # Muestra quién lo generó (puedes cambiar 'username' por 'nombres' si prefieres)
    creado_por = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Reporte
        fields = [
            'id', 
            'titulo', 
            'archivo', 
            'fecha_generacion', 
            'tipo', 
            'tipo_legible',       # Campo calculado
            'fecha_inicio_datos', 
            'fecha_fin_datos',
            'usuario',            # ID del usuario (Read Only)
            'creado_por',         # Nombre del usuario (Read Only)
            'division',           # ID de división (Read Only - Seguridad)
            'division_nombre'     # Nombre de división (Read Only)
        ]
        
        # SEGURIDAD CRÍTICA:
        # Estos campos NO se aceptan en el JSON de entrada.
        # Se llenan automáticamente en el Backend (perform_create).
        read_only_fields = ['usuario', 'division', 'fecha_generacion']
        
# --- SERIALIZER PARA REGISTRO DE USUARIOS (ALTA) ---


class RegistroMaestroSerializer(serializers.ModelSerializer):
    # Campo auxiliar para buscar al maestro (no se guarda en Usuario)
    matricula = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        # LIMPIEZA: Solo pedimos lo necesario para la cuenta
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
        # 1. Separamos los datos
        matricula = validated_data.pop('matricula')
        password = validated_data.pop('password')
        
        # 2. Creamos el Usuario (Solo Auth)
        # create_user se encarga de hashear la contraseña
        user = Usuario.objects.create_user(
            password=password,
            **validated_data # Aquí va username y email
        )

        # 3. VINCULACIÓN: Asignamos este usuario al maestro existente
        maestro = Maestro.objects.get(matricula_m=matricula)
        maestro.usuario = user
        maestro.save()

        return user