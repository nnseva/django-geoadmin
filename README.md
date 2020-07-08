[![Build Status](https://api.travis-ci.com/nnseva/django-geoadmin.svg?branch=master)](https://travis-ci.com/github/nnseva/django-geoadmin)

# Django Geo Admin

The [Django Geo Admin List](https://github.com/nnseva/django-geoadmin) package provides an admin list view
for the geo-based data of the GeoDjango. It requires django-leaflet and uses leaflet to show the map.

## Installation

*Stable version* from the PyPi package repository
```bash
pip install django-geoadmin
```

*Last development version* from the GitHub source version control system
```
pip install git+git://github.com/nnseva/django-geoadmin.git
```

## Configuration

Include the `geoadmin` application into the `INSTALLED_APPS` list, like:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'geoadmin',
    ...
]
```

Use the `GEOADMIN` dictionary option in the settings.py file
to pass options into the Geo Admin:

```python
GEOADMIN = {
    'media': {
        'css': {
            'font-awesome': '//maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css',
            'leaflet': '//unpkg.com/leaflet/dist/leaflet.css',
            'leaflet-contextmenu': '//cdnjs.cloudflare.com/ajax/libs/leaflet-contextmenu/1.4.0/leaflet.contextmenu.min.css',
            'leaflet-responsive-popup': '//unpkg.com/leaflet-responsive-popup@0.6.4/leaflet.responsive.popup.css',
            'beautifymarker': '//cdn.jsdelivr.net/npm/beautifymarker@1.0.7/leaflet-beautify-marker-icon.css',
            'leaflet-mouse-position': '//cdn.jsdelivr.net/npm/leaflet-mouse-position/src/L.Control.MousePosition.css',
            'geoadmin': 'geoadmin/geoadmin.css',
            'additional': [],
        },
        'js': {
            'jquery': '//code.jquery.com/jquery-3.5.1.js',
            'debug': '//cdn.jsdelivr.net/npm/debug/dist/debug.js',
            'leaflet': '//unpkg.com/leaflet/dist/leaflet.js',
            'leaflet-contextmenu': '//cdnjs.cloudflare.com/ajax/libs/leaflet-contextmenu/1.4.0/leaflet.contextmenu.min.js',
            'permalink': '//cdnjs.cloudflare.com/ajax/libs/leaflet-plugins/3.3.1/control/Permalink.min.js',
            'permalink-layer': '//cdnjs.cloudflare.com/ajax/libs/leaflet-plugins/3.3.1/control/Permalink.Layer.min.js',
            'leaflet-responsive-popup': '//unpkg.com/leaflet-responsive-popup@0.6.4/leaflet.responsive.popup.js',
            'beautifymarker': '//cdn.jsdelivr.net/npm/beautifymarker/leaflet-beautify-marker-icon.js',
            'leaflet-mouse-position': '//cdn.jsdelivr.net/npm/leaflet-mouse-position/src/L.Control.MousePosition.js',
            'leaflet-control-custom': '//cdn.jsdelivr.net/npm/leaflet-control-custom/Leaflet.Control.Custom.js',
            'geoadmin': 'geoadmin/geoadmin.js',
            'additional': [],
        }
    },
    'max_window': {
        'lat_size': 0.1,
        'lon_size': 0.1,
    }
}
```

The `media` chapter is used to request the correspondent media on the view page. Use `additional` section for each one
to add your own css and js media to the page.

The `max_window` section describes a maximum size for the request bounding box. This restriction is required to
avoid server overload on too big request bounding box.

## Using

In your admin.py:
```python
...
from leaflet.admin import LeafletGeoAdminMixin
from geoadmin.admin import GeoAdminMixin
...

class WaypointAdmin(GeoAdminMixin, LeafletGeoAdminMixin, ModelAdmin):
    ...
```

## Geo Admin customization

Every Geo Admin may be customized using parameters as well as and method overrides.

### Geo Admin customization parameters

The following Admin class attributes can be used to customize Geo Admin view:

- `geoadmin_view_template` geoadmin page view template
- `geoadmin_attribution` custom data layer attribution, supports HTML
- `geoadmin_max_window_lat_size` override `max_window.lat_size` from settings
- `geoadmin_max_window_lon_size` override `max_window.lon_size` from settings
- `geoadmin_feature_options` per-field options to show them on the page, see the structure below

The `geoadmin_feature_options` attribute is a dictionary with keys corresponding field names.
All content under the key is passed to the page javascript code. The following
keys have a meaning for it:

- `icon` - contains parameters to create a
  [`L.BeautifyIcon.Icon`][https://github.com/masajid390/BeautifyMarker) instance for any point, the
  whole field, or part of the `GeometryCollection` field
- `style` - contains [parameters](https://leafletjs.com/reference-1.6.0.html#path-option) to pass
  to the `style` option for the feature representing fields containing vector graphics

The [`L.BeautifyIcon.Icon`][https://github.com/masajid390/BeautifyMarker) instantiated on the map
has the following attributes:

- `icon` Name of icon you want to show on marker
- `iconSize` Size of marker icon
- `iconAnchor` Anchor size of marker
- `iconShape` Different shapes of marker icon: marker, circle-dot, rectangle, rectangle-dot, doughnut
- `iconStyle` Give any style to marker div
- `innerIconAnchor` Anchor size of font awesome or glyphicon with respect to marker
- `innerIconStyle` Give any style to font awesome or glyphicon (i.e. HTML i tag)
- `isAlphaNumericIcon` This tells either you want to create marker with icon or text
- `text` If isAlphaNumericIcon property set to true, then this property use to add text
- `borderColor` Border color or marker icon
- `borderWidth` Border width of marker icon
- `borderStyle` Border style of marker icon
- `backgroundColor` Background color of marker icon
- `textColor` Text color of marker icon
- `customClasses` Additional custom classes in the created tag
- `spin` - set to true to use glypicon spin instead of the font awesome
- `prefix` According to icon library, f.e. fa or glyphicon
- `html` Create marker by giving own html

The `style` options may have the [following keys](https://leafletjs.com/reference-1.6.0.html#path-option):

- `stroke` Whether to draw stroke along the path. Set it to false to disable borders on polygons or circles.
- `color`  Stroke color
- `weight`  Stroke width in pixels
- `opacity`  Stroke opacity
- `lineCap` A string that defines shape to be used at the end of the stroke.
- `lineJoin` A string that defines shape to be used at the corners of the stroke.
- `dashArray` A string that defines the stroke dash pattern.
- `dashOffset` A string that defines the distance into the dash pattern to start the dash.
- `fill` Whether to fill the path with color. Set it to false to disable filling on polygons or circles.
- `fillColor` Fill color. Defaults to the value of the color option
- `fillOpacity` Fill opacity.
- `fillRule` A string that defines how the inside of a shape is determined.

### Geo Admin URLs

The modified admin has two additional admin URLs and correspondent view methods:

- `/admin/../geoadmin/` URL processed by the `geoadmin_view` function returns the geoadmin page
- `/admin/../geoadmin_api/` URL processed by the `geoadmin_api` function returns the geoadmin JSON API

These methods may be overriden, but sometimes you can override detail API
functions instead to achieve your needs, see below.

### Geo Admin API overrides

Geo Admin uses structured JSON API to get objects from the database and show them on the map.

Sequentional processing of API request allows to customize all details of objects detailzations.
The following methods of the Admin class may be overriden to modify output:

- `def geoadmin_api(self, request)` is a main view function of the API
- `def geoadmin_serialize(self, request, queryset)` gets the base queryset
  of all avilable objects and returns serialized response content
- `def geoadmin_list_json(self, request, queryset)` gets control from the function above
  and returns structured json-like response object to be returned back
- `def geoadmin_params(self, request, queryset, fields)` - extracts request parameters
- `def geoadmin_max_window_size(self, request, queryset)` - returns max window size
- `def geoadmin_initial(self, request, queryset, fields)` - returns initial position
  to use when no any parameters are passed to the request (should never be happened, except
  direct or external request to the geoadmin API)
- `def geoadmin_list_objects(self, request, queryset, fields, south, west, north, east)`
  returns final `list` of objects to be returned
- `def geoadmin_json(self, request, object, field_names)` - translates the passed object
  to the structured value to be returned
- `def geoadmin_url(self, request, object)` - returns a reference URL for the object
  to be shown on the map to get link to the object shown
- `def geoadmin_geojson(self, request, object, field_names)` - returns GeoJSON representation
  of the objects
- `def geoadmin_geojson_feature(self, request, object, field_name)` - returns GeoJSON Feature
  representing one field of the object
- `def geoadmin_geojson_feature_geometry(self, request, object, field_name)` - returns the
  GeoJSON Feature Geometry part
- `def geoadmin_geojson_feature_properties(self, request, object, field_name)` - returns
  the GeoJSON Feature poperties attribute
- `def geoadmin_geojson_feature_options(self, request, object, field_name)` - returns the
  the GeoJSON Feature `icon` and `style` options as described for `geoadmin_feature_options`
- `def geoadmin_title(self, request, object)` - returns a title for the object
- `def geoadmin_fields(self, request)` - returns list of field names
