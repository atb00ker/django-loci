from django.conf.urls import url
from django_loci.channels.consumers import LocationBroadcast
from django_loci.channels.base import location_broadcast_path
# Channels
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

channel_routing = ProtocolTypeRouter({ 
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(location_broadcast_path, LocationBroadcast, name='LocationBroadcast')
                ]
            )
        ),
    )
})


# # channel_routing = [LocationBroadcast.as_route(path=location_broadcast_path)]
# channel_routing = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             url(r'^/ws/loci/location/(?P<pk>[^/]+)/$', LocationBroadcast, name='LocationBroadcast')
#             # path(location_broadcast_path, LocationBroadcast, name),
#         ]),
#     ),
# })
