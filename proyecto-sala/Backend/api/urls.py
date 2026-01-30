from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView 
from django.conf import settings              
from django.conf.urls.static import static   


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from reservas.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api-auth/login/', admin.site.login, name='login'),
    path('api-auth/', include('rest_framework.urls')),
    
    path('api/v1/', include('reservas.urls')),
    
    path('', RedirectView.as_view(url='/api/v1/', permanent=False)),
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)