import socketio
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

sio = socketio.AsyncServer(
    async_mode='asgi', cors_allowed_origins="*", logger=True, engineio_logger=True)

users = {}
socket_to_room = {}


class CallNamespace(socketio.AsyncNamespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.room_id = None

    def on_connect(self, sid, environ):
        pass
    
    async def on_ready(self, sid, data):
        print('ready')
        await sio.emit('ready', data, room=self.room_id, namespace='/room')
        
    async def on_join_room(self, sid, room_id, peer_id):
        self.room_id = room_id
        sio.enter_room(sid, room_id, namespace='/room')

        print(sio.rooms(sid, namespace='/room'))
        
        # this method returns sid and other id of each participant
        participants = list(sio.manager.get_participants(namespace='/room', room=room_id)) 
        
        # this method returns only sid of each participant
        users_in_this_room = [user[0] for user in participants] # this method returns only sid of each participant
        # print(f'USERS IN THIS ROOM: {users_in_this_room}')

        await sio.emit('user-connected', peer_id, room=room_id, skip_sid=sid, namespace='/room')
        await sio.emit('users-connected', users_in_this_room, room=room_id, namespace='/room')
        


    async def on_sending_signal(self, sid, data):
        # print(f'signal received -->  {data}')
        await sio.emit("user joined", data, room=data["userToSignal"], namespace='/room')

    async def on_returning_signal(self, sid, data):
        await sio.emit("receiving returned signal", data, room=data["callerID"], namespace='/room')

    async def on_disconnect(self, sid):
        sio.leave_room(sid, self.room_id, namespace='/room')
        await sio.emit('user-disconnected', sid, room=self.room_id, namespace='/room')


sio.register_namespace(CallNamespace('/room'))
