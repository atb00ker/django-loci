import importlib
from ..models import Location, ObjectLocation
from .testdeviceapp.models import Device
from channels.auth import AuthMiddlewareStack
import asynctest
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import Permission
from . import TestAdminMixin, TestLociMixin
from ..channels.base import _get_object_or_none
from ..channels.consumers import LocationBroadcast
from ..channels.routing import channel_routing
from ..models import Location, ObjectLocation
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.conf import settings
from django.http.request import HttpRequest
from channels.db import database_sync_to_async
from django.test import TestCase
from django.core import serializers



class TestChannels(TestAdminMixin, TestLociMixin, TestCase, asynctest.TestCase):

    def setUp(self):
        self.object_model = Device
        self.location_model = Location
        self.object_location_model = ObjectLocation
        self.user_model = get_user_model()


    async def force_login(self, user, backend=None):
        engine = importlib.import_module(settings.SESSION_ENGINE)
        request = HttpRequest()
        request.session = engine.SessionStore()
        login(request, user, backend)
        request.session.save
        return request.session

    # async def test_object_or_none(self):
    #     result = await _get_object_or_none(self.location_model, pk=1)
    #     self.assertEqual(result, None)
    #     plausible_pk = self.location_model().pk
    #     result = await _get_object_or_none(self.location_model, pk=plausible_pk)
    #     self.assertEqual(result, None)

    # async def _send_post_request(self, user, session, pk, coordinates):
    #     self.client.force_login(user)
    #     form_data = {"created": "2018-08-28T15:38:27.339Z", "modified": "2018-08-28T15:38:27.342Z", "name": "test-location", "type": "outdoor", "is_mobile":"on", "address": "Via del Corso, Roma, Italia", "geometry": "SRID=4326;POINT (12.513124 41.897903)", "form-TOTAL_FORMS": 1, "form-INITIAL_FORMS": 0 }
    #     request_url = "/admin/django_loci/location/{0}/change/".format(pk)

    #     # post the request without any change
    #     response = self.client.post(request_url, form_data)



        response = self.client.post(request_url, form_data)
        self.assertEqual(response.status_code, 302)
    
    async def _test_consume(self, pk=None, user=None):
        if not pk:
            location = self._create_location(is_mobile=True)
            self._create_object_location(location=location)
            pk = location.pk
        path = '/ws/loci/location/{0}/'.format(pk)
        communicator = WebsocketCommunicator(LocationBroadcast, '/ws/loci/location/{0}/'.format(pk))
        if user:
            session = await self.force_login(user)
            communicator.scope.update({
                "user": user, 
                "session": session, 
                "url_route": {
                    "kwargs": {
                        "pk": pk
                        }
                    }
                })
        connected, subprotocol = await communicator.connect()
        return {'pk': pk, 'path': path, 'connected': connected, 'communicator': communicator}

    
    # async def test_consumer_unauthenticated(self):
    #     response = await self._test_consume()
    #     self.assertFalse(response['connected'])

    # async def test_connect_and_disconnect(self):
    #     response = await self._test_consume(user=self._create_admin())
    #     self.assertTrue(response['connected'])
    #     communicator = response['communicator']
    #     await communicator.disconnect()
        
    # async def test_consumer_not_staff(self):
    #     user = self.user_model.objects.create_user(username='user',
    #                                                password='password',
    #                                                email='test@test.org')
    #     response =  await self._test_consume(user=user)
    #     self.assertFalse(response['connected'])
    #     communicator = response['communicator']
    #     await communicator.disconnect()

    # async def test_consumer_staff_but_no_change_permission(self):
    #     user = self.user_model.objects.create_user(username='user_staff',
    #                                                password='password',
    #                                                email='test@test.org',
    #                                                is_staff=True)
    #     location = self._create_location(is_mobile=True)
    #     ol = self._create_object_location(location=location)
    #     pk = ol.location.pk
    #     response = await self._test_consume(pk=pk, user=user)
    #     self.assertFalse(response['connected'])
    #     communicator = response['communicator']
    #     await communicator.disconnect()
        # add permission to change location and repeat
        # perm = Permission.objects.filter(name='Can change location').first()
        # user.user_permissions.add(perm)
        # response = await self._test_consume(pk=pk, user=user)
        # self.assertTrue(response['connected'])
        # await communicator.disconnect()

    # async def test_consumer_404(self):
    #     pk = self.location_model().pk
    #     response = await self._test_consume(pk=pk, user=self._create_admin())
    #     self.assertTrue(response['connected'])
    #     communicator = response['communicator']
    #     await communicator.disconnect()
            

    async def test_location_update(self):
        response = await self._test_consume(user=self._create_admin())
        communicator = response['communicator']
        # Change Location
        # await self._send_post_request(
        #     user=communicator.scope["user"],
        #     session=communicator.scope["session"],
        #     pk=response['pk'],
        #     coordinates='POINT (12.513124 41.897903)'
        # )
        # response = communicator.receive_json_from(timeout=5)
        location = self.location_model.objects.get(pk=response['pk'])
        location.geometry = 'POINT (12.513124 41.897903)'
        location.save()
        # Get Response form WebSocket
        
        # self.assertIsInstance(result, dict)
        # self.assertDictEqual(result, {'type': 'Point', 'coordinates': [12.513124, 41.897903]})
        # await communicator.disconnect()

# class TestChannels(BaseTestChannels):
#     object_model = Device
#     location_model = Location
#     object_location_model = ObjectLocation
#     user_model = get_user_model()
