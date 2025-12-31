import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ReservaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1. Definimos un nombre para el "grupo" de chat
        # Todos los que estén conectados a este grupo recibirán las actualizaciones
        self.room_group_name = "reservas_updates"

        # 2. Unimos al usuario actual a ese grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 3. Aceptamos la conexión WebSocket
        await self.accept()
        print(f"Conexión WebSocket aceptada: {self.channel_name}")

    async def disconnect(self, close_code):
        # Cuando se desconectan, los sacamos del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Este método se ejecuta cuando el grupo recibe un mensaje (desde Django)
    # y se encarga de reenviarlo al Frontend (Vue.js)
    async def reserva_update(self, event):
        message = event['message']

        # Enviamos los datos al WebSocket (al navegador)
        await self.send(text_data=json.dumps({
            'message': message
        }))
