from django.conf import settings


DEFAULT = {
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
    },
}


def get_option(name, default=None):
    """
        Reads option by the full name separated by the dot character
        from settings or from the default settings
    """
    names = name.split('.')
    actual = get_option_from(getattr(settings, 'GEOADMIN', {}), names)
    default_option = get_option_from(DEFAULT, names)
    if actual is None:
        if default_option is None:
            return default
        return default_option
    return actual


def get_option_from(options, path):
    """Reads option from options by the name path, returns None if not found"""
    path = list(path)
    while path:
        n = path.pop(0)
        if n not in options:
            return
        options = options[n]
    return options
