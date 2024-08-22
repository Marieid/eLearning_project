import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from eLearning_app import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eLearning_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            eLearning_app.routing.websocket_urlpatterns
        )
    ),
})
