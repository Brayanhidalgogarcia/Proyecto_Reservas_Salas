"""
Configuración ASGI para el proyecto.

Expone la aplicación ASGI como una variable a nivel de módulo llamada ``application``.
Enruta las peticiones HTTP estándar a través del núcleo de Django y las conexiones 
WebSocket a través de Django Channels, aplicando capas de seguridad y autenticación.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# 1. Configuración de entorno base
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# 2. Inicialización Temprana (Crítico)
# Se debe llamar a get_asgi_application() ANTES de importar enrutadores locales 
# para evitar la excepción django.core.exceptions.AppRegistryNotReady.
django_asgi_app = get_asgi_application()

# 3. Importaciones Locales (Post-inicialización)
from reservas.routing import websocket_urlpatterns  # noqa: E402

# 4. Definición del Enrutador Principal
application = ProtocolTypeRouter({
    
    # Manejador para tráfico HTTP tradicional (REST API)
    "http": django_asgi_app,

    # Manejador para tráfico en tiempo real (WebSockets)
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})