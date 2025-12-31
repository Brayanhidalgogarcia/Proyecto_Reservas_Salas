import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from reservas import routing

# IMPORTANTE: Aquí apuntamos a 'api.settings' porque ahí está tu configuración
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Inicializamos la aplicación Django ASGI para HTTP
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Django maneja las peticiones HTTP normales (vistas, API, admin)
    "http": django_asgi_app,

    # Aquí manejaremos los WebSockets
    # Por ahora lo dejamos vacío hasta que creemos el "Consumer" en la Fase 2
    "websocket": AuthMiddlewareStack(
        URLRouter(
             routing.websocket_urlpatterns
        )
    ),
})
        