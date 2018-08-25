from django_loci.channels.consumers import LocationBroadcast
from django_loci.channels.base import location_broadcast_path
from django.urls import path
# Channels
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


# channel_routing = [LocationBroadcast.as_route(path=location_broadcast_path)]
channel_routing = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path(location_broadcast_path, LocationBroadcast),
        ]),
    ),
})