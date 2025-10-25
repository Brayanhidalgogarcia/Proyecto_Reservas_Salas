from rest_framework import serializers
from .models import Division, Asignatura, Sala, Maestro, Reserva, PerfilAdministrador
from django.contrib.auth.models import User

class PerfilAdministradorSerializer(serializers.ModelSerializer):
  
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PerfilAdministrador
        fields = ['user', 'matricula_ud', 'telefono', 'division', 'username', 'email']


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'


class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = '__all__'


class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__'


class MaestroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maestro
        fields = '__all__'


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
