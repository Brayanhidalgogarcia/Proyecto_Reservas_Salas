from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

from reservas.views import RegistroUsuarioView


router = DefaultRouter()


router.register(r'divisiones', views.DivisionViewSet)
router.register(r'asignaturas', views.AsignaturaViewSet)
router.register(r'salas', views.SalaViewSet)
router.register(r'maestros', views.MaestroViewSet)
router.register(r'reservas', views.ReservaViewSet)
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'reportes', views.ReporteViewSet, basename='reportes')


urlpatterns = [
    path('', include(router.urls)),
    path('admin/registro-usuario/', RegistroUsuarioView.as_view(), name='registro_usuario'),
]