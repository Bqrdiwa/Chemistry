"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from main.routing import websocket_urlpatterns as ROUTERS
from dj_static import Cling, MediaCling
from static_ranges import Ranges

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
    {
        'http':asgi_app,
        'websocket':AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                   ROUTERS
                )
            )
        )
    }
)