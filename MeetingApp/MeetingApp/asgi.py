"""
ASGI config for MeetingApp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import socketio
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from api.sockets import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MeetingApp.settings')

django_asgi_app = get_asgi_application()

application = socketio.ASGIApp(sio, django_asgi_app)
