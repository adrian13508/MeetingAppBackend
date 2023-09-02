from channels.routing import ProtocolTypeRouter, URLRouter
# import app.routing
from django.urls import re_path
#from api.consumers import VideoConsumer
from api.consumers import TextRoomConsumer

websocket_urlpatterns = [
    #re_path(r'^ws/(?P<room_name>[^/]+)/$', VideoConsumer.as_asgi()),
    re_path(r'^ws/(?P<room_name>[^/]+)/$', TextRoomConsumer.as_asgi()),
]
