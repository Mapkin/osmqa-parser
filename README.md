osmqa-parser
============

An [imposm parser](https://github.com/omniscale/imposm) for
[OSM QA tiles](https://osmlab.github.io/osm-qa-tiles/). `osmqa-parser` was
written for use with [tile-reduce-py](https://github.com/jwass/tile-reduce-py)
and [osmgraph](https://github.com/mapkin/osmgraph).


Usage
-----
The parser should be used with an `imposm` importer such as the one found in
`osmgraph`.


Data Model Caveats
------------------
OSM QA tiles are delivered as
[Mapbox Vector Tiles](https://www.mapbox.com/developers/vector-tiles/). It is
impossible to exactly reconstruct the original OSM data from a vector tile.
And they are not designed for this use case.

Because ways in a QA tile contain a coordinate sequence instead of a node
sequence, we can't distinguish different nodes that have the same tile
coordinate. `osmqa-parser` assigns unique node IDs based on tile coordinate.
As a result, it's possible we introduce false intersections which arise when
two ways have different nodes that have the same coordinates.


Goes Great With
---------------
* [osmgraph](https://github.com/mapkin/osmgraph)
* [imposm](https://github.com/omniscale/imposm)
* [tile-reduce-py](https://github.com/jwass/tile-reduce-py)


See Also
--------
* [Mapbox Vector Tiles](https://www.mapbox.com/developers/vector-tiles/)
* [imposm-parser](https://github.com/omniscale/imposm-parser)
