import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_{self.room_name}'

        # Join the room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('signalData'):
            # Handle signaling data (SDP or ICE candidates)
            signal_data = data['signalData']
            await self.send_signal(signal_data)

        if data.get('acceptCall'):
            # Handle call acceptance
            await self.send_acceptance(data['callerID'], data['signalData'])

    async def send_signal(self, signal_data):
        # Forward signaling data to other clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'forward_signal',
                'signal_data': signal_data,
                'sender_channel_name': self.channel_name
            }
        )

    async def forward_signal(self, event):
        # Forward signaling data to the recipient client
        sender_channel_name = event['sender_channel_name']
        signal_data = event['signal_data']

        await self.send(text_data=json.dumps({
            'signalData': signal_data,
            'userFrom': sender_channel_name == self.channel_name
        }))

    async def send_acceptance(self, caller_id, signal_data):
        # Send call acceptance signal to the caller
        await self.send(text_data=json.dumps({
            'callAccepted': True,
            'signalData': signal_data,
        }))
