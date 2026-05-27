from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission, SAFE_METHODS

from .models import Division, Asignatura, Sala, Maestro, Reserva, Usuario, Reporte,Actividad,Edificio
from .serializers import (
    DivisionSerializer, AsignaturaSerializer, SalaSerializer, 
    MaestroSerializer, ReservaSerializer, UsuarioSerializer, 
    ReporteSerializer, RegistroMaestroSerializer, ActividadSerializer, EdificioSerializer
)

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser
    
class EdificioViewSet(viewsets.ModelViewSet):
    serializer_class = EdificioSerializer 
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser:
            return Edificio.objects.all()
            
        # Extraemos la división del usuario
        division_usuario = None
        if hasattr(user, 'division') and user.division:
            division_usuario = user.division
        elif hasattr(user, 'perfil_maestro') and user.perfil_maestro:
            division_usuario = user.perfil_maestro.division

        if division_usuario:
            return Edificio.objects.filter(division=division_usuario)
            
        return Edificio.objects.none()


class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class SalaViewSet(viewsets.ModelViewSet):
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        
        # El superusuario ve todas las salas con su ruta completa
        if user.is_superuser:
            return Sala.objects.select_related('edificio__division').all()

        # Detección de la división del usuario activo
        division_usuario = None
        if hasattr(user, 'division') and user.division:
            division_usuario = user.division
        elif hasattr(user, 'perfil_maestro') and user.perfil_maestro:
            division_usuario = user.perfil_maestro.division

        # El candado: Solo salas cuyo edificio pertenezca a la división del usuario
        if division_usuario:
            return Sala.objects.filter(edificio__division=division_usuario).select_related('edificio__division')
            
        return Sala.objects.none()
    
class ActividadViewSet(viewsets.ModelViewSet):
    serializer_class = ActividadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        
        return Actividad.objects.filter(activo=True)

class MaestroViewSet(viewsets.ModelViewSet):
    queryset = Maestro.objects.all()
    serializer_class = MaestroSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=user.id)
class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated] 

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
                raise ValidationError({
                    "detail": f"Error de Identidad: El usuario '{user.username}' no está vinculado a ningún registro de Maestro. Contacta al administrador."
                })
    
    def perform_update(self, serializer):
        user = self.request.user
        reserva_original = self.get_object()

        if not user.is_superuser and reserva_original.creado_por != user:
             raise ValidationError({"detail": "No tienes permiso para editar una reserva que no es tuya."})
        
        if not user.is_superuser:
             if hasattr(user, 'perfil_maestro') and user.perfil_maestro:
                serializer.save(maestro=user.perfil_maestro)
             else:
                raise ValidationError({"detail": "Error: Usuario sin perfil de maestro vinculado."})
        else:
             serializer.save()

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
        user = self.request.user
        
        # 1. Optimización profunda: Ahora viaja hasta la división
        queryset = Reserva.objects.select_related(
            'sala__edificio__division', 'maestro', 'asignatura', 'actividad'
        ).all().order_by('-inicio') 
        
        # 2. EL ESCUDO DE AISLAMIENTO
        if not user.is_superuser:
            division_usuario = None
            if hasattr(user, 'division') and user.division:
                division_usuario = user.division
            elif hasattr(user, 'perfil_maestro') and user.perfil_maestro:
                division_usuario = user.perfil_maestro.division

            if division_usuario:
                queryset = queryset.filter(sala__edificio__division=division_usuario)
            else:
                # Si es un usuario sin perfil asignado, no ve ninguna reserva por seguridad
                return Reserva.objects.none()

        # 3. Filtros dinámicos solicitados por Vue.js
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        sala_id = self.request.query_params.get('sala')
        actividad_id = self.request.query_params.get('actividad') 
        
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

        if actividad_id:
            queryset = queryset.filter(actividad_id=actividad_id)

        return queryset

class ReporteViewSet(viewsets.ModelViewSet):
    serializer_class = ReporteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        
       
        if user.is_superuser:
            queryset = Reporte.objects.all()
        else:
          
            division = None
            if hasattr(user, 'division'): 
                division = user.division
            elif hasattr(user, 'perfil_maestro') and user.perfil_maestro:
                division = user.perfil_maestro.division

            if not division:
                return Reporte.objects.none()

            queryset = Reporte.objects.filter(division=division)

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

        if hasattr(user, 'perfil_maestro') and user.perfil_maestro:
             division_destino = user.perfil_maestro.division
        elif hasattr(user, 'division'):
             division_destino = user.division

       
        if not division_destino:
            from .models import Division
            division_destino = Division.objects.first()

        if not division_destino:
            raise ValidationError({"error": "No hay divisiones registradas en el sistema."})

        serializer.save(
            usuario=user,
            division=division_destino
        )

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [IsAdminUser] 
    serializer_class = RegistroMaestroSerializer