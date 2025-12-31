from rest_framework import viewsets
from rest_framework.response import Response
from .models import Division, Asignatura, Sala, Maestro, Reserva, PerfilAdministrador
from .serializers import (
    DivisionSerializer, AsignaturaSerializer, SalaSerializer, 
    MaestroSerializer, ReservaSerializer, PerfilAdministradorSerializer
)
from datetime import datetime



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

class PerfilAdministradorViewSet(viewsets.ModelViewSet):
    queryset = PerfilAdministrador.objects.all()
    serializer_class = PerfilAdministradorSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def get_queryset(self):
        
        queryset = Reserva.objects.all().order_by('-inicio') 

       
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        sala_id = self.request.query_params.get('sala')
        
     
        if fecha_inicio and fecha_fin:
            try:
              
                queryset = queryset.filter(
                    inicio__date__gte=fecha_inicio, 
                    inicio__date__lte=fecha_fin     
                )
            except ValueError:
                pass 

        
        if sala_id:
            queryset = queryset.filter(sala__clave_sala=sala_id)

        return queryset