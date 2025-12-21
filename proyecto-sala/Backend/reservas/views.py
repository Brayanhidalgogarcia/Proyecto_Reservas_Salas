from rest_framework import viewsets
from .models import (Division, Asignatura, Sala, Maestro, 
Reserva,
PerfilAdministrador)
from .serializers import (DivisionSerializer, AsignaturaSerializer, SalaSerializer, MaestroSerializer, 
                          ReservaSerializer, 
                          PerfilAdministradorSerializer)



class PerfilAdministradorViewSet(viewsets.ModelViewSet):
  
    queryset = PerfilAdministrador.objects.all()
    serializer_class = PerfilAdministradorSerializer


class DivisionViewSet(viewsets.ModelViewSet):
    
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer


class AsignaturaViewSet(viewsets.ModelViewSet):
   
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer


class SalaViewSet(viewsets.ModelViewSet):
  
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer


class MaestroViewSet(viewsets.ModelViewSet):
   
    queryset = Maestro.objects.all()
    serializer_class = MaestroSerializer


class ReservaViewSet(viewsets.ModelViewSet):

    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
