from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/', include('reservas.urls')),
    
    
     path('', RedirectView.as_view(url='/api/v1/', permanent=False)),
]
