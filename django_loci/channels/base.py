from channels.generic.websocket import WebsocketConsumer
# from channels.consumer import SyncConsumer    
from django.core.exceptions import ValidationError
from asgiref.sync import async_to_sync

location_broadcast_path = r'^ws/loci/location/(?P<pk>[^/]+)/$'


def _get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (ValidationError, model.DoesNotExist):
        return None


class BaseLocationBroadcast(WebsocketConsumer):
    """
    Notifies that the coordinates of a location have changed
    to authorized users (superusers or organization operators)
    """
    http_user = True
    def websocket_connect(self, message):
        user = self.scope["user"]
        self.pk = self.scope['url_route']['kwargs']['pk']
        location = _get_object_or_none(self.model, pk=self.pk)
        if not location or not self.is_authorized(user, location):
            return
        async_to_sync(self.channel_layer.group_add)(
            'loci.mobile-location.{0}'.format(self.pk), 
            self.channel_name
        )
        self.accept()

    def is_authorized(self, user, location):
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

    def websocket_disconnect(self, message):
        """
        Perform things on connection close
        """
        async_to_sync(self.channel_layer.group_discard)(
            'loci.mobile-location.{0}'.format(self.pk), 
            self.channel_name
        )