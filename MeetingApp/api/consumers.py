import json

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class VideoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"room_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "offer":
            await self.send_offer(data)
        elif message_type == "answer":
            await self.send_answer(data)
        elif message_type == "candidate":
            await self.send_candidate(data)

    async def send_offer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "offer_message",
                "data": data,
            },
        )

    async def send_answer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "answer_message",
                "data": data,
            },
        )

    async def send_candidate(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "candidate_message",
                "data": data,
            },
        )

    async def offer_message(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def answer_message(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def candidate_message(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))


class TextRoomConsumer(WebsocketConsumer):
    def connect(self):
        # gets 'room_name' and open websocket connection
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json['text']
        sender = text_data_json['sender']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text,
                'sender': sender
            }
        )

    
    def chat_message(self, event):
        # Receive message from room group
        text = event['message']
        sender = event['sender']

        # broadcast message to all clients in WebSocket
        self.send(text_data=json.dumps({
            'text': text,
            'sender': sender
        }))
