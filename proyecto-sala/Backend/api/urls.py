"""
Configuración de URLs principal (Root URLconf).
Rutea las peticiones HTTP hacia los distintos módulos de la aplicación,
incluyendo el panel de administración, la API REST (v1) y la generación
de tokens JWT para la autenticación de usuarios.
"""

# ==========================================
# 1. IMPORTS DE DJANGO
# ==========================================
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView 
from django.conf import settings              
from django.conf.urls.static import static   

# ==========================================
# 2. IMPORTS DE TERCEROS (Simple JWT)
# ==========================================
from rest_framework_simplejwt.views import TokenRefreshView

# ==========================================
# 3. IMPORTS LOCALES
# ==========================================
from rest_framework_simplejwt.views import TokenObtainPairView
from reservas.serializers import CustomTokenObtainPairSerializer

# ==========================================
# VISTAS PERSONALIZADAS
# ==========================================
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para la generación inicial de tokens JWT.
    Utiliza el CustomTokenObtainPairSerializer para inyectar claims adicionales
    (como el rol del usuario, division, etc.) directamente dentro de la 
    firma del token (payload), reduciendo peticiones subsecuentes al backend.
    """
    serializer_class = CustomTokenObtainPairSerializer


# ==========================================
# PATRONES DE RUTAS (URL PATTERNS)
# ==========================================
urlpatterns = [
    
    # Redirección de la raíz del servidor hacia la API REST
    path('', RedirectView.as_view(url='/api/v1/', permanent=False), name='index'),
    
    # ----------------------------------------
    # MÓDULOS DEL ADMINISTRADOR (Django Core)
    # ----------------------------------------
    path('admin/', admin.site.urls),
    path('api-auth/login/', admin.site.login, name='api-login'),
    path('api-auth/', include('rest_framework.urls')),
    
    # ----------------------------------------
    # ENDPOINTS DE NEGOCIO (App Reservas)
    # ----------------------------------------
    # Todas las rutas declaradas en reservas/urls.py estarán bajo el prefijo /api/v1/
    path('api/v1/', include('reservas.urls')),
    
    # ----------------------------------------
    # ENDPOINTS DE SEGURIDAD (Manejo de Sesión JWT)
    # ----------------------------------------
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]

# ==========================================
# ARCHIVOS MULTIMEDIA (Solo para Desarrollo)
# ==========================================
# Permite a Django servir archivos estáticos locales (como los PDF de tus reportes)
# cuando DEBUG=True. En producción, esto se gestiona desde el servidor web (ej. Nginx).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)