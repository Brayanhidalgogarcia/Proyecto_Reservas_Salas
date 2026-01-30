from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView 
from django.conf import settings               # <--- IMPORTANTE
from django.conf.urls.static import static     # <--- IMPORTANTE


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Importamos nuestro Serializer personalizado
from reservas.serializers import CustomTokenObtainPairSerializer

# Creamos una vista personalizada que use nuestro Serializer
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/', include('reservas.urls')),
    
    path('', RedirectView.as_view(url='/api/v1/', permanent=False)),
    
    # CAMBIO AQUÍ: Usamos CustomTokenObtainPairView en lugar de la genérica
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)