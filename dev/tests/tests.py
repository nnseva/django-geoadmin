from __future__ import absolute_import, print_function

import json

from six import text_type
from tests.admin import WaypointAdmin
from tests.models import Building, DeliveryJob, Waypoint

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import Client, TestCase

from geoadmin import __version__ as version


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
                waypoint=Point([50 + i / 100, 50 + (10 - i) / 100 + 0.5])
            )
            for i in range(1, 10)
        ]

        self.delivery_jobs = [
            DeliveryJob.objects.create(
                name='Delivery Test %s' % i,
                pickup_point=Point([50 + i / 100, 50 + (10 - i) / 100]),
                dropoff_point=Point([50 + (10 - i) / 100, 50 + i / 100]),
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

    def test_006_instance_details_refers_geoadmin(self):
        """Test whether the instance detail admin page refers geoadmin map"""
        c = Client()
        c.login(username='user', password='password')
        wp = self.waypoints[0]
        response = c.get('/admin/tests/waypoint/%s/change/' % wp.pk)
        self.assertIn('/admin/tests/waypoint/geoadmin#lat=%s&lon=%s' % (wp.waypoint.y, wp.waypoint.x), text_type(response.content))

    def test_007_geoadmin_api_default(self):
        """Test whether the geoadmin api returns some reasonable defaults if requested without parameters"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/waypoint/geoadmin_api')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        content = json.loads(response.content)
        self.assertIn('meta', content)
        self.assertIn('objects', content)
        self.assertEqual(content['meta']['total'], 9)
        self.assertLess(content['meta']['count'], 9)
        self.assertEqual(len(content['objects']), content['meta']['count'])

    def test_008_geoadmin_api_restrict_big_area(self):
        """Test whether the geoadmin api restricts big area to the customizable reasonable values"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/waypoint/geoadmin_api?south=40&north=60&west=45&east=55')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        content = json.loads(response.content)
        self.assertIn('meta', content)
        self.assertIn('warning', content['meta'])
        self.assertIn('objects', content)
        self.assertEqual(content['meta']['total'], 9)
        self.assertGreater(content['meta']['south'], 40)
        self.assertLess(content['meta']['north'], 60)
        self.assertGreater(content['meta']['west'], 45)
        self.assertLess(content['meta']['east'], 55)

    def test_009_null_value_processed(self):
        """Test whether the null value is processed fine"""
        c = Client()
        c.login(username='user', password='password')
        b = Building.objects.create(name='qwerty')
        response = c.get('/admin/tests/building/%s/change/' % b.pk)
        self.assertIn('No coordinates', text_type(response.content))

    def test_010_no_objects_processed(self):
        """Test whether the geoadmin works properly with empty queryset"""
        c = Client()
        c.login(username='user', password='password')
        response = c.get('/admin/tests/building/geoadmin_api')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        content = json.loads(response.content)
        self.assertIn('meta', content)
        self.assertIn('objects', content)
        self.assertEqual(content['meta']['total'], 0)
        self.assertEqual(content['meta']['count'], 0)
        self.assertEqual(len(content['objects']), content['meta']['count'])
