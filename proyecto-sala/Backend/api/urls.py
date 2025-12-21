from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('servicios/v1/', include('reservas.urls')),
    
    
     path('', RedirectView.as_view(url='/servicios/v1/', permanent=False)),
]
