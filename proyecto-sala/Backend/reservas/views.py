from rest_framework import viewsets
from rest_framework.response import Response
from .models import Division, Asignatura, Sala, Maestro, Reserva, PerfilAdministrador
from .serializers import (
    DivisionSerializer, AsignaturaSerializer, SalaSerializer, 
    MaestroSerializer, ReservaSerializer, PerfilAdministradorSerializer
)
from datetime import datetime

# --- VISTAS EXISTENTES ---

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

# --- VISTA DE RESERVAS MEJORADA (CON FILTROS) ---
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def get_queryset(self):
        
        queryset = Reserva.objects.all().order_by('-inicio') # Ordenar por las más recientes

        # 1. Obtener parámetros de la URL (Query Params)
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        sala_id = self.request.query_params.get('sala')
        
        # 2. Filtrar por Rango de Fechas
        if fecha_inicio and fecha_fin:
            try:
                # Convertir strings 'YYYY-MM-DD' a objetos fecha si es necesario, 
                # pero Django suele manejar strings ISO automáticamente en filtros __date.
                queryset = queryset.filter(
                    inicio__date__gte=fecha_inicio, # Mayor o igual a fecha_inicio
                    inicio__date__lte=fecha_fin     # Menor o igual a fecha_fin
                )
            except ValueError:
                pass # Si las fechas vienen mal, ignoramos el filtro

        # 3. Filtrar por Sala Específica
        if sala_id:
            queryset = queryset.filter(sala__clave_sala=sala_id)

        return queryset