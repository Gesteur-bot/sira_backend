"""
Configuration ASGI pour Sira.

ASGI permet de gérer HTTP (Django classique) ET WebSocket (Channels)
sur un seul serveur. C'est ce qui permet le suivi temps réel des courses.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# Charger Django avant d'importer Channels
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

# Les URL WebSocket seront ajoutées par les apps métier
# (par exemple apps.rides aura des routes pour le suivi GPS)
websocket_urlpatterns = []

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})