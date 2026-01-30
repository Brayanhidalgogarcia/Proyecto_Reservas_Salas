from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Division, Asignatura, Sala, Maestro, Reserva, Usuario,Reporte
from .serializers import (
    DivisionSerializer, AsignaturaSerializer, SalaSerializer, 
    MaestroSerializer, ReservaSerializer, UsuarioSerializer,ReporteSerializer
)
from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser

# --- VISTAS DE CATÁLOGOS ---
# (Asumimos que todos los usuarios autenticados pueden ver/editar catálogos)
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

# --- VISTA DE USUARIOS (SEGURIDAD AUMENTADA) ---
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

        # --- BLINDAJE DE SEGURIDAD ---
        
        if user.is_superuser:
            # CASO 1: EL JEFE (ADMIN)
            # Confiamos en él. Si eligió un maestro en el formulario, lo respetamos.
            # Solo añadimos la firma de "creado_por".
            serializer.save(creado_por=user)
        else:
            # CASO 2: EL MAESTRO (USUARIO MORTAL)
            # No confiamos en lo que envíe en el campo 'maestro'. 
            # Forzamos que la reserva sea para SU perfil vinculado.
            
            # Verificamos si existe el vínculo que creamos en models.py (related_name='perfil_maestro')
            if hasattr(user, 'perfil_maestro') and user.perfil_maestro:
                serializer.save(
                    creado_por=user,
                    maestro=user.perfil_maestro  # <--- AQUÍ ESTÁ EL CANDADO: Sobreescribimos el maestro
                )
            else:
                # Si el usuario existe pero no está vinculado a ningún maestro, bloqueamos la acción.
                raise ValidationError({"detail": "Error de Seguridad: Tu usuario no está vinculado a un perfil de Maestro válido."})

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
    
# --- VIEWSET DE REPORTES ---
class ReporteViewSet(viewsets.ModelViewSet):
    """
    Maneja la lógica de negocio para los Reportes Generados.
    Seguridad: Solo accesible por Administradores.
    """
    serializer_class = ReporteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Regla de Escalabilidad:
        Un administrador solo puede ver los reportes de SU propia división.
        """
        user = self.request.user
        
        # Validación de seguridad: Si el usuario no tiene división asignada (raro, pero posible),
        # retornamos una lista vacía para evitar errores o fugas de datos.
        if not hasattr(user, 'division') or not user.division:
            return Reporte.objects.none()

        # Filtro base: Solo reportes de mi división
        queryset = Reporte.objects.filter(division=user.division)

        # --- FILTROS DE INTELIGENCIA DE NEGOCIOS (BI) ---
        # Permite al Frontend filtrar sin descargar todo
        
        # 1. Filtrar por Tipo (Ej: ?tipo=OCUPACION)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        # 2. Filtrar por año/mes de generación (Ej: ?anio=2025)
        anio = self.request.query_params.get('anio')
        if anio:
            queryset = queryset.filter(fecha_generacion__year=anio)

        return queryset.order_by('-fecha_generacion')

    def perform_create(self, serializer):
        """
        Automatización:
        Al crear un reporte, asignamos automáticamente:
        1. El usuario actual (autor).
        2. La división del usuario actual (contexto).
        Esto evita que el Frontend pueda falsificar estos datos.
        """
        user = self.request.user
        
        if not hasattr(user, 'division') or not user.division:
            # Aquí podrías lanzar un ValidationError si es crítico que tenga división
            pass 

        serializer.save(
            usuario=user,
            division=user.division
        )