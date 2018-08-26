import channels.layers
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django_loci.channels.consumers import LocationBroadcast
from django.db.models.signals import post_save


def send_message(event):
    '''
    Call back function to send message to the browser
    '''
    message = event['text']
    channel_layer = channels.layers.get_channel_layer()
    # Send message to WebSocket
    async_to_sync(channel_layer.send)(message, immediately=True)


def update_mobile_location(sender, instance, **kwargs):
    if not kwargs.get('created') and instance.geometry:
        group_name = 'loci.mobile-location.{0}'.format(str(instance.pk))
        message = {'text': instance.geometry.geojson}
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_message',
                'text': message
            }
        )

def load_location_receivers(sender):
    """
    enables signal listening when called
    designed to be called in AppConfig subclasses
    """
    # using decorator pattern with old syntax
    # in order to decorate an existing function
    receiver(
        post_save,
        sender=sender,
        dispatch_uid='ws_update_mobile_location'
    )(update_mobile_location)
