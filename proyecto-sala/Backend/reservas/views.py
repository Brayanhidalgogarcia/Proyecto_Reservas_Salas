from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser

from .models import Division, Asignatura, Sala, Maestro, Reserva, Usuario, Reporte
from .serializers import (
    DivisionSerializer, AsignaturaSerializer, SalaSerializer, 
    MaestroSerializer, ReservaSerializer, UsuarioSerializer, 
    ReporteSerializer, RegistroMaestroSerializer
)


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


class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=user.id)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def perform_create(self, serializer):
        user = self.request.user

      
        
        if user.is_superuser:
           
            serializer.save(creado_por=user)
        else:
            
            
           
            if hasattr(user, 'perfil_maestro') and user.perfil_maestro:
                serializer.save(
                    creado_por=user,
                    maestro=user.perfil_maestro  
                )
            else:
               
                raise ValidationError({"detail": "Error de Seguridad: Tu cuenta de usuario no está vinculada a ningún perfil de Maestro activo."})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        es_admin = request.user.is_superuser
        es_dueno = instance.creado_por == request.user
        
        if not (es_admin or es_dueno):
            return Response(
                {"detail": "No tienes permiso para eliminar esta reserva. Solo el autor o un administrador pueden hacerlo."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        return super().destroy(request, *args, **kwargs)

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


class ReporteViewSet(viewsets.ModelViewSet):
    """
    Maneja la lógica de negocio para los Reportes Generados.
    Seguridad: Solo accesible por Administradores.
    """
    serializer_class = ReporteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        
        if not hasattr(user, 'division') or not user.division:
            return Reporte.objects.none()

        queryset = Reporte.objects.filter(division=user.division)

        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        anio = self.request.query_params.get('anio')
        if anio:
            queryset = queryset.filter(fecha_generacion__year=anio)

        return queryset.order_by('-fecha_generacion')

    def perform_create(self, serializer):
        user = self.request.user
        division_destino = None

        if hasattr(user, 'division') and user.division:
            division_destino = user.division
        
      
        if not division_destino:
            from .models import Division
            division_destino = Division.objects.first()

        if not division_destino:
            raise ValidationError({"error": "No hay divisiones registradas."})

        serializer.save(
            usuario=user,
            division=division_destino
        )


class RegistroUsuarioView(generics.CreateAPIView):
    """
    Endpoint PROTEGIDO. 
    Solo un usuario logueado como Administrador (IsAdminUser) puede usarlo 
    para dar de alta a un maestro y vincularlo.
    """
    queryset = Usuario.objects.all()
    permission_classes = [IsAdminUser] 
    serializer_class = RegistroMaestroSerializer