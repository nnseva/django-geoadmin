from __future__ import absolute_import, print_function

import json

from six import text_type
from tests.admin import WaypointAdmin
from tests.models import DeliveryJob, Waypoint

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import Client, TestCase as _TestCase

from geoadmin import __version__ as version


class TestCase(_TestCase):
    """Compatibility fix"""
    if not hasattr(_TestCase, 'assertRegex'):
        assertRegex = _TestCase.assertRegexpMatches
    if not hasattr(_TestCase, 'assertNotRegex'):
        assertNotRegex = _TestCase.assertNotRegexpMatches


class ModuleTest(TestCase):
    maxDiff = None

    def setUp(self):
        """Sets the test environment"""
        self.user = User.objects.create(username='user', is_superuser=True, is_staff=True)
        self.user.set_password('password')
        self.user.save()

        self.waypoints = [
            Waypoint.objects.create(
                name='Waypoint Test %s' % i,
                waypoint=Point([i / 100, (10 - i) / 100 + 0.5])
            )
            for i in range(1, 10)
        ]

        self.delivery_jobs = [
            DeliveryJob.objects.create(
                name='Delivery Test %s' % i,
                pickup_point=Point([i / 100, (10 - i) / 100]),
                dropoff_point=Point([(10 - i) / 100, i / 100]),
                kind='wood',
            )
            for i in range(1, 10)
        ]

    def test_001_admin_page_present(self):
        """Test whether the geoadmin view is present"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/waypoint/geoadmin')
        self.assertIn('<title>Map of Waypoints | Django site admin</title>', text_type(response.content))
        response = c.get('/admin/tests/waypoint/geoadmin/')
        self.assertIn('<title>Map of Waypoints | Django site admin</title>', text_type(response.content))

    def test_002_admin_link(self):
        """Test whether the geoadmin URL is linked from the admin list"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/waypoint/')
        self.assertRegex(text_type(response.content),
            r'href\="/admin/tests/waypoint/geoadmin".*Map of Waypoints'
        )

    def test_003_admin_link_back(self):
        """Test whether the admin list is linked from the geoadmin URL"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/waypoint/geoadmin')
        self.assertRegex(text_type(response.content),
            r'href\="/admin/tests/waypoint/".*Waypoints'
        )

    def test_004_geoadmin_api(self):
        """Test whether the geoadmin api works with single point and bbox properly"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/waypoint/geoadmin_api', data={
            'south': self.waypoints[0].waypoint.y - 0.0001,
            'west': self.waypoints[0].waypoint.x - 0.0001,
            'north': self.waypoints[0].waypoint.y + 0.0001,
            'east': self.waypoints[0].waypoint.x + 0.0001,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        content = json.loads(response.content)
        self.assertEqual(content, {
            "meta": {
                "total": 9,
                "count": 1,
                "south": self.waypoints[0].waypoint.y - 0.0001,
                "west": self.waypoints[0].waypoint.x - 0.0001,
                "north": self.waypoints[0].waypoint.y + 0.0001,
                "east": self.waypoints[0].waypoint.x + 0.0001,
                "version": version,
            },
            "objects": [
                {
                    "pk": self.waypoints[0].pk,
                    "title": str(self.waypoints[0]),
                    "url": "/admin/tests/waypoint/%s/change/" % self.waypoints[0].pk,
                    "geo": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        self.waypoints[0].waypoint.x,
                                        self.waypoints[0].waypoint.y
                                    ]
                                },
                                "properties": {
                                    "name": "waypoint",
                                    "verbose_name": "Waypoint",
                                    "options": WaypointAdmin.geoadmin_feature_options['waypoint']
                                }
                            }
                        ]
                    }
                }
            ]
        })
        response = c.get('/admin/tests/waypoint/geoadmin_api', data={
            'south': self.waypoints[5].waypoint.y - 0.015,
            'west': self.waypoints[5].waypoint.x - 0.015,
            'north': self.waypoints[5].waypoint.y + 0.015,
            'east': self.waypoints[5].waypoint.x + 0.015,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        content = json.loads(response.content)
        self.assertEqual(content['meta']['count'], 3)
        self.assertEqual(content['meta']['total'], 9)
        self.assertEqual(set([p['pk'] for p in content['objects']]), set(w.pk for w in self.waypoints[4:7]))

    def test_005_geoadmin_api_multiple(self):
        """Test whether the geoadmin api works with multiple properties and bbox properly"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/deliveryjob/geoadmin_api', data={
            'south': self.delivery_jobs[6].pickup_point.y - 0.015,
            'west': self.delivery_jobs[6].pickup_point.x - 0.015,
            'north': self.delivery_jobs[6].pickup_point.y + 0.015,
            'east': self.delivery_jobs[6].pickup_point.x + 0.015,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        content = json.loads(response.content)
        self.assertEqual(content['meta']['count'], 6)
        self.assertEqual(content['meta']['total'], 9)
        self.assertEqual(set([f['properties']['name'] for f in content['objects'][0]['geo']['features']]), {'pickup_point', 'dropoff_point'})
        self.assertEqual(set([p['pk'] for p in content['objects']]), set([w.pk for w in self.delivery_jobs[1:4] + self.delivery_jobs[5:8]]))
