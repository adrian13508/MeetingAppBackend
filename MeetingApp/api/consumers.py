# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"call_{self.room_name}"

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
        message_type = data['type']

        if message_type == 'join_room':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'join_room',
                    'username': data['username'],
                }
            )
        elif message_type == 'offer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer',
                    'offer': data['offer'],
                }
            )
        elif message_type == 'answer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'answer',
                    'answer': data['answer'],
                }
            )
        elif message_type == 'ice_candidate':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'candidate': data['candidate'],
                }
            )

    async def join_room(self, event):
        username = event['username']

        # Send a welcome message to the connected user
        await self.send(text_data=json.dumps({
            'type': 'join_room',
            'username': username,
        }))

    async def offer(self, event):
        offer = event['offer']

        # Send the offer to all other users in the room
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': offer,
        }))

    async def answer(self, event):
        answer = event['answer']

        # Send the answer to all other users in the room
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': answer,
        }))

    async def ice_candidate(self, event):
        candidate = event['candidate']

        # Send the ICE candidate to all other users in the room
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': candidate,
        }))
