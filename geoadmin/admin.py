import json

from django import forms
from django.contrib.gis.geos import MultiPoint, Polygon
from django.db.models import Q
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .options import get_option
from .version import __version__


class GeoAdminMixin(object):
    #: overriding list view default template
    change_list_template = 'geoadmin/geoadmin_change_list.html'
    #: geoadmin default template
    geoadmin_view_template = get_option('template')

    #: geoadmin additional options per field
    geoadmin_feature_options = {}
    #: geoadmin maximal coordinates diff to avoid overload on high zoom
    geoadmin_max_window_lat_size = get_option('max_window.lat_size')
    geoadmin_max_window_lon_size = get_option('max_window.lon_size')

    geoadmin_attribution = None

    def get_urls(self):
        """Overriden to add necessary admin URLs"""
        from django.conf.urls import url
        from functools import update_wrapper

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^geoadmin_api(?:/?)$',
                wrap(self.geoadmin_api),
                name='%s_%s_geoadmin_api' % info),
            url(r'^geoadmin(?:/?)$',
                wrap(self.geoadmin_view),
                name='%s_%s_geoadmin_view' % info),
        ]
        urls = super().get_urls()
        return urlpatterns + urls

    def geoadmin_api(self, request):
        """Geoadmin API entry point"""
        r = HttpResponse(self.geoadmin_serialize(request, self.get_queryset(request)))
        r['Content-Type'] = 'application/json'
        return r

    def geoadmin_serialize(self, request, queryset):
        """Geoadmin API data serializer"""
        js = self.geoadmin_list_json(request, queryset)
        return json.dumps(js)

    def geoadmin_list_json(self, request, queryset):
        """Geoadmin API data extractor"""
        fields = self.geoadmin_fields(request)
        south, west, north, east = self.geoadmin_params(request, queryset, fields)
        warning = None
        north_south = abs(north - south)
        east_west = abs(east - west)
        geoadmin_max_window_lat_size, geoadmin_max_window_lon_size = self.geoadmin_max_window_size(request, queryset)
        if north_south >= geoadmin_max_window_lat_size or east_west >= geoadmin_max_window_lon_size:
            warning = str(_('Visible objects area has been restricted'))
            if north_south >= geoadmin_max_window_lat_size:
                north = south + (north_south + geoadmin_max_window_lat_size) / 2
                south = south + (north_south - geoadmin_max_window_lat_size) / 2
            if east_west >= geoadmin_max_window_lon_size:
                east = west + (east_west + geoadmin_max_window_lon_size) / 2
                west = west + (east_west - geoadmin_max_window_lon_size) / 2
        lst = self.geoadmin_list_objects(request, queryset, fields, south, west, north, east)
        return {
            'meta': {
                'total': queryset.count(),
                'version': __version__,
                'count': len(lst),
                'south': south,
                'west': west,
                'north': north,
                'east': east,
                **({'warning': warning} if warning else {})
            },
            'objects': [self.geoadmin_json(request, o, fields) for o in lst]
        }

    def geoadmin_max_window_size(self, request, queryset):
        """Returns geoadmin API max window"""
        return self.geoadmin_max_window_lat_size, self.geoadmin_max_window_lon_size

    def geoadmin_params(self, request, queryset, fields):
        """Geoadmin API parameters translator"""
        latlon = self.geoadmin_initial(request, queryset, fields)
        west = max(float(request.GET.get('west', latlon[1] - 0.01)), -179.9999999999)
        south = max(float(request.GET.get('south', latlon[0] - 0.01)), -89.9999999999)
        east = min(float(request.GET.get('east', latlon[1] + 0.01)), 180)
        north = min(float(request.GET.get('north', latlon[0] + 0.01)), 90)
        return south, west, north, east

    def geoadmin_initial(self, request, queryset, fields):
        """Geoadmin API default parameters"""
        # TODO
        if queryset:
            instance = queryset[0]
        else:
            return 0, 0
        bb = MultiPoint([getattr(instance, f).centroid for f in fields]).extent
        return (bb[3] + bb[1]) / 2., (bb[2] + bb[0]) / 2.

    def geoadmin_list_objects(self, request, queryset, fields, south, west, north, east):
        """Geoadmin API data requester"""
        q_filter = Q()
        for field_name in fields:
            q_filter = q_filter | Q(**{
                '%s__intersects' % field_name: Polygon([
                    (west, south), (west, north),
                    (east, north), (east, south),
                    (west, south)
                ], srid=4326)
            })
        queryset = queryset.filter(q_filter)
        return list(queryset)

    def geoadmin_json(self, request, o, field_names):
        """Geoadmin API object data extractor"""
        return {
            'pk': o.pk,
            'title': self.geoadmin_title(request, o),
            'url': self.geoadmin_url(request, o),
            'geo': self.geoadmin_geojson(request, o, field_names),
            **(
                {'absolute_url': o.get_absolute_url()}
                if hasattr(o, 'get_absolute_url')
                else {}
            )
        }

    def geoadmin_url(self, request, o):
        """Geoadmin API object reference URL generator"""
        info = self.model._meta.app_label, self.model._meta.model_name
        return reverse('admin:%s_%s_change' % info, args=(o.pk,))

    def geoadmin_geojson(self, request, o, field_names):
        """Geoadmin API object geojson extractor"""
        return {
            'type': 'FeatureCollection',
            'features': [f for f in [
                self.geoadmin_geojson_feature(request, o, f)
                for f in field_names
            ] if f is not None]
        }

    def geoadmin_geojson_feature(self, request, o, field_name):
        """Geoadmin API object geojson feature extractor"""
        return {
            'type': 'Feature',
            'geometry': self.geoadmin_geojson_feature_geometry(request, o, field_name),
            'properties': self.geoadmin_geojson_feature_properties(request, o, field_name)
        }

    def geoadmin_geojson_feature_geometry(self, request, o, field_name):
        """Geoadmin API object geojson feature geometry extractor"""
        return json.loads(getattr(o, field_name).json)

    def geoadmin_geojson_feature_properties(self, request, o, field_name):
        """Geoadmin API object geojson feature properties extractor"""
        return {
            'name': field_name,
            'verbose_name': str(self.model._meta.get_field(field_name).verbose_name),
            'options': self.geoadmin_geojson_feature_options(request, o, field_name)
        }

    def geoadmin_geojson_feature_options(self, request, o, field_name):
        """Geoadmin API object geojson feature options extractor"""
        return self.geoadmin_feature_options.get(field_name, {})

    def geoadmin_title(self, request, o):
        """Geoadmin API object title extractor"""
        return str(o)

    def geoadmin_fields(self, request):
        """Geoadmin API object fields extractor"""
        from django.contrib.gis.db import models
        return [
            f.name for f in self.model._meta.fields
            if isinstance(f, models.GeometryField) and f.geography
        ]

    def geoadmin_view(self, request):
        """Main Geoadmin View"""
        opts = self.model._meta
        info = self.model._meta.app_label, self.model._meta.model_name

        context = {
            **self.admin_site.each_context(request),
            'module_name': str(opts.verbose_name_plural),
            'title': _('Map of %(name_plural)s') % {
                'name_plural': opts.verbose_name_plural,
            },
            'media': self.media + self.geoadmin_media(request),
            'opts': opts,
            'cl': {'opts': opts},
            # map
            'id_map': 'geoadmin',
            'fetch_url': reverse('admin:%s_%s_geoadmin_api' % info),
            'version': __version__,
            'attribution': self.geoadmin_attribution,
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.geoadmin_view_template or [
            'geoadmin/%s/%s/geoadmin_view.html' % info,
            'geoadmin/%s/geoadmin_view.html' % info[0],
            'geoadmin/geoadmin_view.html'
        ], context)

    def geoadmin_media(self, request):
        """Geoadmin View media"""
        add_css = tuple(get_option('media.css.additional', []))
        add_js = tuple(get_option('media.js.additional', []))
        return forms.Media(
            css={
                'all': (
                    get_option('media.css.font-awesome', ''),
                    get_option('media.css.leaflet', ''),
                    get_option('media.css.leaflet-contextmenu', ''),
                    get_option('media.css.leaflet-responsive-popup', ''),
                    get_option('media.css.beautifymarker', ''),
                    get_option('media.css.leaflet-mouse-position', ''),
                    get_option('media.css.geoadmin', ''),
                ) + add_css
            },
            js=(
                get_option('media.js.jquery', ''),
                get_option('media.js.debug', ''),
                get_option('media.js.leaflet', ''),
                get_option('media.js.leaflet-contextmenu', ''),
                get_option('media.js.permalink', ''),
                get_option('media.js.permalink-layer', ''),
                get_option('media.js.leaflet-responsive-popup', ''),
                get_option('media.js.beautifymarker', ''),
                get_option('media.js.leaflet-mouse-position', ''),
                get_option('media.js.leaflet-control-custom', ''),
                get_option('media.js.geoadmin', ''),
            ) + add_js
        )
