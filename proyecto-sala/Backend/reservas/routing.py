from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Definimos la ruta para conectar el socket
    # El frontend se conectará a: ws://localhost:8000/ws/reservas/
    re_path(r'ws/reservas/$', consumers.ReservaConsumer.as_asgi()),
]
