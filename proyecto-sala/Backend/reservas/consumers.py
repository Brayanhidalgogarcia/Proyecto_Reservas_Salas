import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ReservaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        self.room_group_name = "reservas_updates"

       
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        
        await self.accept()
        print(f"Conexión WebSocket aceptada: {self.channel_name}")

    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    
    async def reserva_update(self, event):
        message = event['message']

       
        await self.send(text_data=json.dumps({
            'message': message
        }))
