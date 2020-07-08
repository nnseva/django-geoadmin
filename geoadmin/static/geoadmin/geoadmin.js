// Enabling console messages
//
// debug.enable("geoadmin:*")
// debug.enable("geoadmin:error")
// debug.enable("geoadmin:info")
// debug.enable("geoadmin:debug")

if(typeof($) == 'undefined')
    $ = jQuery;
GeoObjectListLayer = L.LayerGroup.extend({
    initialize: function(options) {
        L.Util.setOptions(this, options);
        var that = this;
        var opts = {};
        if( typeof(options.attribution) != 'undefined' ) {
            opts.attribution = options.attribution;
        }
        L.LayerGroup.prototype.initialize.call(this, [], opts);
    },
    onAdd: function(map) {
        this.map = map;
        var that = this;
        this.map.on('resize move zoom', function() {
            that.schedule_fetch(500);
        })
        this.schedule_fetch(500);
    },
    fetchUrl: function() {
        return this.options.url;
    },
    schedule_fetch: function(milliseconds) {
        var that = this;
        if(typeof(this._scheduled_fetch) != 'undefined') {
            clearTimeout(this._scheduled_fetch);
            delete this._scheduled_fetch;
        }
        this._scheduled_fetch = setTimeout(function() {
            clearTimeout(that._scheduled_fetch);
            that.fetch();
        }, milliseconds);
    },
    fetch: function() {
        var that = this;
        return $.ajax({
            url: that.fetchUrl(),
            data: {
                north: that.map.getBounds().getNorth(),
                south: that.map.getBounds().getSouth(),
                east: that.map.getBounds().getEast(),
                west: that.map.getBounds().getWest(),
            },
        }).then(function(v) {
            that.clearLayers();
            if(typeof(that._warning) != 'undefined') {
                that._warning.remove();
                delete that._warning;
            }
            if( typeof(v.meta.warning) != 'undefined' ) {
                that._warning = L.control.custom({
                    position: 'topright',
                    content: v.meta.warning,
                    style: {opacity: 0.7, background: 'white'},
                }).addTo(that.map);
            }
            that.addLayer(L.rectangle(
                [[v.meta.south, v.meta.east], [v.meta.north, v.meta.west]],
                {
                    'stroke': true,
                    'color': 'green',
                    'weight': 1,
                    'dashArray': '1 5',
                    'fill': false,
                    'bubblingMouseEvents': false,
                }
            ))
            return $.when($.map(v.objects, function(options,k) {
                return that.addGeoObject(options);
            }))
        })
    },
    addGeoObject: function(options) {
        debug("geoobject:debug")("GeoObjectList: add",options);
        var that = this;
        this.addLayer(
            L.geoJSON(
                options.geo,
                {
                    pointToLayer: function(geoJsonPoint, latlng) {
                        return L.marker(latlng, {
                            icon: L.BeautifyIcon.icon(geoJsonPoint.properties.options.icon),
                        })
                    },
                    style: function(geoJsonFeature) {
                        return geoJsonFeature.properties.options.style;
                    },
                    onEachFeature: function(feature, layer) {
                        layer.bindTooltip(that.featureTooltipContent(options, feature))
                    }
                },
            ).bindPopup(
                L.responsivePopup().setContent(
                     that.geoObjectPopupContent(options)
                )
            )
        );
    },
    featureTooltipContent: function(options, feature) {
        return '<b>' + options.title + '</b><br/>' +
            '<ul><li>' + feature.properties.verbose_name +
            '</ul>';
    },
    geoObjectPopupContent: function(options) {
        var content = '<a href="'+options.url+'" target="_blank">'+
                    options.title+
                    '</a><b/><br/>';
        return content;
    },
})
