from rest_framework import serializers
from .models import (Division, Asignatura, Sala, Maestro, 
                     Reserva, 
                     PerfilAdministrador)
from django.contrib.auth.models import User



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
    
        response = super().to_representation(instance)
        
    
        response['maestro'] = str(instance.maestro)
        response['asignatura'] = str(instance.asignatura)
        response['sala'] = str(instance.sala)
        
        return response