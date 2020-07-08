from __future__ import absolute_import, print_function

from leaflet.admin import LeafletGeoAdminMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from geoadmin.admin import GeoAdminMixin

from .models import Building, DeliveryJob, Waypoint


class WaypointAdmin(GeoAdminMixin, LeafletGeoAdminMixin, ModelAdmin):
    list_display = ["name", ]
    geoadmin_max_window_lon_size = 0.2
    geoadmin_feature_options = {
        'waypoint': {
            'icon': {
                'icon': '',
                'iconSize': [10, 10],
                'iconAnchor': [5, 5],
                'borderColor': 'red',
                'textColor': 'black',
                'iconShape': 'circle',
                'popupAnchor': [0, -11],
            },
        },
    }

    class Media:
        pass


admin.site.register(Waypoint, WaypointAdmin)


class DeliveryJobAdmin(GeoAdminMixin, LeafletGeoAdminMixin, ModelAdmin):
    list_display = ["name", "quantity", "weight", "price", "kind"]
    geoadmin_feature_options = {
        'pickup_point': {
            'icon': {
                'icon': 'upload',
                'borderColor': 'red',
                'textColor': 'black',
                'iconShape': 'circle',
                'popupAnchor': [0, -11],
            },
        },
        'dropoff_point': {
            'icon': {
                'icon': 'download',
                'borderColor': 'red',
                'textColor': 'black',
                'iconShape': 'circle',
                'popupAnchor': [0, -11],
            },
        },
    }


admin.site.register(DeliveryJob, DeliveryJobAdmin)


class BuildingAdmin(GeoAdminMixin, LeafletGeoAdminMixin, ModelAdmin):
    list_display = ["name", ]
    geoadmin_feature_options = {
        'geometry': {
            'icon': {
                'icon': 'upload',
                'borderColor': 'green',
                'textColor': 'black',
                'iconShape': 'circle',
                'popupAnchor': [0, -11],
            },
            'style': {
                'color': 'green',
                'fillColor': 'gray',
            }
        }
    }


admin.site.register(Building, BuildingAdmin)
