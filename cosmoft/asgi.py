"""
ASGI config for cosmoft project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from django.urls import path  

from maills import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cosmoft.settings")

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    "websocket": SessionMiddlewareStack( 
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('ws/emails/', consumers.MessageConsumer.as_asgi()),
                ]
            )
        )
    ),
})

