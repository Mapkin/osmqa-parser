from __future__ import division

import itertools
import math

import mapbox_vector_tile


class QATileParser(object):
    def __init__(self,
                 nodes_callback=None, ways_callback=None,
                 relations_callback=None, coords_callback=None,
                 nodes_tag_filter=None, ways_tag_filter=None,
                 relations_tag_filter=None, marshal_elem_data=False):
        self.nodes_callback = nodes_callback
        self.ways_callback = ways_callback
        self.coords_callback = coords_callback
        self.nodes_tag_filter = nodes_tag_filter
        self.ways_tag_filter = ways_tag_filter

        self.x = None
        self.y = None
        self.zoom = None
        self.extent = None

        self.node_id_seq = itertools.count()
        self.node_id_map = {}  # Map (lon, lat) to node ID
        self.way_id_seq = itertools.count()

    def parse_data(self, data, x, y, zoom):
        self.x = x
        self.y = y
        self.zoom = zoom

        tile = mapbox_vector_tile.decode(data)
        self.extent = tile['osm']['extent']
        for feature in tile['osm']['features']:
            self._handle_feature(feature)

    def _handle_feature(self, feature):
        if feature['properties'].get('_osm_node_id'):
            self._handle_node(feature)
        elif feature['properties'].get('_osm_way_id'):
            self._handle_way(feature)
        else:
            raise ValueError('Unknown type from feature %s' % feature)

    def _handle_node(self, feature):
        if not self.nodes_callback and not self.coords_callback:
            return

        x, y = feature['geometry'][0]
        lon, lat = self.to_lonlat(x, y)
        node_id = self._add_coords(lon, lat)

        if self.nodes_callback:
            tags = feature['properties']
            if self.nodes_tag_filter:
                self.nodes_tag_filter(tags)
            if tags:
                self.nodes_callback([(node_id, tags, (lon, lat))])

    def _handle_way(self, feature):
        if not self.ways_callback:
            return
        if self.ways_tag_filter:
            self.ways_tag_filter(feature['properties'])
        if not feature['properties']:
            return

        g = feature['geometry']
        d = depth(g)
        if d == 2:
            lines = [g]
        elif d == 3:
            lines = g
        else:
            raise ValueError('Depth %d' % d)

        for line in lines:
            node_ids = []
            for (x, y) in line:
                lon, lat = self.to_lonlat(x, y)
                node_id = self._add_coords(lon, lat)
                node_ids.append(node_id)

            way = (next(self.way_id_seq), feature['properties'], node_ids)
            self.ways_callback([way])

    def _add_coords(self, lon, lat):
        node_id = self.node_id_map.get((lon, lat))
        if node_id is None:
            node_id = next(self.node_id_seq)
            self.node_id_map[(lon, lat)] = node_id
            if self.coords_callback:
                self.coords_callback([(node_id, lon, lat)])
        return node_id

    def to_lonlat(self, x, y):
        return to_lonlat(self.x, self.y, self.zoom, self.extent, x, y)


def depth(c):
    try:
        float(c)
        return 0
    except TypeError:
        return 1 + depth(c[0])


def to_lonlat(tile_x, tile_y, tile_zoom, tile_extent, x, y):
    y = tile_extent - y  # Mapzen flips the y coordinate so flip it back
    n_cells_side = 2**tile_zoom * tile_extent

    x_normalized = (x + tile_x * tile_extent) / n_cells_side - 0.5
    lon = x_normalized * 360.

    y_normalized = 0.5 - (y + tile_y * tile_extent) / n_cells_side
    lat = math.degrees(math.atan(math.sinh(2 * math.pi * y_normalized)))

    return lon, lat
