from rest_framework import serializers
from .models import (Division, Asignatura, Sala, Maestro, 
                     Reserva, 
                     PerfilAdministrador)
from django.contrib.auth.models import User
from django.utils import timezone




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PerfilAdministradorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PerfilAdministrador
        fields = ['user', 'matricula_ud', 'nombre', 'apellido_p', 'apellido_m', 'telefono', 'division', 'username', 'email', 'correo']

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
    class Meta:
        model = Maestro
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
       
        response['division'] = str(instance.division) 
        return response


class ReservaSerializer(serializers.ModelSerializer):
    division = serializers.StringRelatedField(source='sala.division', read_only=True)

    class Meta:
        model = Reserva
        fields = ['id', 'maestro', 'asignatura', 'sala', 'division', 'tema', 'inicio', 'fin', 'fecha_apartado']

    def to_representation(self, instance):
        # Mantenemos esto EXACTAMENTE como te funcionaba antes.
        # No agregamos 'sala_id' extra para evitar el error de atributo.
        response = super().to_representation(instance)
        
        response['maestro'] = str(instance.maestro)
        response['asignatura'] = str(instance.asignatura)
        response['sala'] = str(instance.sala)
        
        return response

    def validate(self, data):
        """
        Validaciones de seguridad: Se ejecutan solo al CREAR o EDITAR.
        No afectan la visualización de la lista de reservas.
        """
        sala = data.get('sala')
        inicio = data.get('inicio')
        fin = data.get('fin')

        # 1. Validación de coherencia
        if inicio >= fin:
            raise serializers.ValidationError({
                "detail": "La hora de inicio debe ser anterior a la hora de fin."
            })

        # 2. Validación de Horario (08:00 - 16:00)
        # Convertimos a hora local para verificar correctamente
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

        # 3. Validación de SOLAPAMIENTO
        qs = Reserva.objects.filter(
            sala=sala,
            inicio__lt=fin,
            fin__gt=inicio
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            conflicto = qs.first()
            
            # Formato de hora amigable para el mensaje de error
            inicio_mx = timezone.localtime(conflicto.inicio)
            fin_mx = timezone.localtime(conflicto.fin)
            
            h_ini = inicio_mx.strftime('%H:%M')
            h_fin = fin_mx.strftime('%H:%M')
            
            # Usamos 'detail' para que tu Frontend lo muestre en la alerta roja
            raise serializers.ValidationError({
                "detail": f"Conflicto: La sala ya está ocupada por {conflicto.maestro} de {h_ini} a {h_fin}."
            })

        return data