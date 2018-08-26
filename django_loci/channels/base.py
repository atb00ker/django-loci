import asyncio
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

location_broadcast_path = r'^ws/loci/location/(?P<pk>[^/]+)/$'

@database_sync_to_async
def _get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (ValidationError, model.DoesNotExist):
        return None

class BaseLocationBroadcast(AsyncConsumer):
    """
    Notifies that the coordinates of a location have changed
    to authorized users (superusers or organization operators)
    """

    async def websocket_connect(self, crequest):
        """
        Perform action when WebSocket connection
        is opened.
        """
        try:
            user = self.scope["user"]
            self.pk = self.scope['url_route']['kwargs']['pk']
        except Exception as Error:
            # Will fall here when the scope does not have 
            # one of the variables, most commonly, user
            # (When a user tries to access without loggin in)
            await self.send({
                "type": "websocket.close"
            })
            return
        location = _get_object_or_none(self.model, pk=self.pk)
        authorized = await self.is_authorized(user, location)
        if not location or not authorized:
            await self.send({
                "type": "websocket.close"
            })
            return
        await self.channel_layer.group_add(
            'loci.mobile-location.{0}'.format(self.pk), 
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })

    async def send_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def is_authorized(self, user, location):
        perm = '{0}.change_location'.format(self.model._meta.app_label)
        authenticated = user.is_authenticated
        if callable(authenticated):
            authenticated = authenticated()
        return authenticated and (
            user.is_superuser or (
                user.is_staff and
                user.has_perm(perm)
            )
        )

    async def websocket_disconnect(self, crequest):
        """
        Perform things on connection close
        """
        await self.channel_layer.group_discard(
            'loci.mobile-location.{0}'.format(self.pk), 
            self.channel_name
        )