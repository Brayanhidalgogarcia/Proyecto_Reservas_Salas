from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'perfiles', views.PerfilAdministradorViewSet)
router.register(r'divisiones', views.DivisionViewSet)
router.register(r'asignaturas', views.AsignaturaViewSet)
router.register(r'salas', views.SalaViewSet)
router.register(r'maestros', views.MaestroViewSet)
router.register(r'reservas', views.ReservaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
