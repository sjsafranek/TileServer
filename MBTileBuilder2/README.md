# Georeferencing Floor Plans
## Settings
 - Projection: ESPG: 3857
 - Nearest Neighbor
 - Polynomial 1

# Install Dependencies
 - pip install mapnik
 - pip install Tilestache

# Run Server
 - python tilestache-server.py -p <PORT> -c <CONFIG_FILE>

# MB Tile Builder
 - Get bounding box
 - slider to set min and max zoom level
 - build mbtiles
