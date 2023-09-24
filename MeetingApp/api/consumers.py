# api/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This method is called when a WebSocket connection is established.
        # You can perform any setup or authentication here.
        await self.accept()

    async def disconnect(self, close_code):
        # This method is called when a WebSocket connection is closed.
        # You can perform cleanup or other actions here.
        pass

    async def receive(self, text_data):
        # This method is called when the server receives a message from the client.
        # You can process the message and send a response if needed.
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send a response back to the client
        await self.send(text_data=json.dumps({
            'message': 'You said: ' + message
        }))
