import pytest
import asyncio
import asynctest
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import Permission

from .. import TestAdminMixin, TestLociMixin
from ...channels.base import _get_object_or_none
from ...channels.consumers import LocationBroadcast
from ...models import Location, ObjectLocation

class BaseTestChannels(TestAdminMixin, TestLociMixin, asynctest.TestCase):

    # def test_consumer_staff_but_no_change_permission(self):
    #     user = self.user_model.objects.create_user(username='user',
    #                                                password='password',
    #                                                email='test@test.org',
    #                                                is_staff=True)
    #     location = self._create_location(is_mobile=True)
    #     ol = self._create_object_location(location=location)
    #     pk = ol.location.pk
    #     try:
    #         self._test_consume(pk=pk, user=user)
    #     except AssertionError as e:
    #         self.assertIn('Connection rejected', str(e))
    #     else:
    #         self.fail('AssertionError not raised')
    #     # add permission to change location and repeat
    #     perm = Permission.objects.filter(name='Can change location').first()
    #     user.user_permissions.add(perm)
    #     self._test_consume(pk=pk, user=user)

    # def test_consumer_404(self):
    #     pk = self.location_model().pk
    #     admin = self._create_admin()
    #     try:
    #         self._test_consume(pk=pk, user=admin)
    #     except AssertionError as e:
    #         self.assertIn('Connection rejected', str(e))
    #     else:
    #         self.fail('AssertionError not raised')

    # def test_location_update(self):
    #     res = self._test_consume(user=self._create_admin())
    #     loc = self.location_model.objects.get(pk=res['pk'])
    #     loc.geometry = 'POINT (12.513124 41.897903)'
    #     loc.save()
    #     result = self.client.receive()
    #     self.assertIsInstance(result, dict)
    #     self.assertDictEqual(result, {'type': 'Point', 'coordinates': [12.513124, 41.897903]})
