""" 

    Source:
        https://github.com/rshk/render-tiles


"""

from collections import namedtuple
import math
import os
import glob
import mapnik
# from osgeo import ogr
# from osgeo import osr
from flask import Flask
from flask import render_template
from flask import Response
from flask import request

# HANDLING IMAGE FILE UPLOADS
from werkzeug import secure_filename

# GEOTIFFS FOR UPLOADS
from PIL import Image
import subprocess

# UUID FOR UPLOADS
import time
import tempfile
from base64 import urlsafe_b64encode
from uuid import uuid4

# PUBLIC IP
from urllib2 import urlopen


# app = Flask('tileserver')
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MASTERKEY'] = "stefanrocks"
# app.config['SERVER_NAME'] = "dev"



# ============================================================
#                            UTILS                            
# ============================================================

def get_ip():
    return ""
    #return urlopen('http://ip.42.pl/raw').read()

def generate_uuid():
    """ generates uuid """
    chars = urlsafe_b64encode(uuid4().bytes)[0:22].decode()
    code = ''
    for char in chars:
        if char in 'abcdefghijklmnopqrstuvwxyz123456789':
            code += char
    return code

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



# ============================================================
#                      MAP TILE SETTINGS                      
# ============================================================

MIN_ZOOM_LEVEL = 1
MAX_ZOOM_LEVEL = 22

def _unitsPerPixel(zoomLevel):
    return 0.703125 / math.pow(2, zoomLevel)

# Google Mercator - EPSG:900913
GOOGLEMERC = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
              '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
DATA_PROJECTION = mapnik.Projection(GOOGLEMERC)
TILE_WIDTH = 256
TILE_HEIGHT = 256

def deg2num(lat_deg, lon_deg, zoom):
    """Convert coordinates to tile number"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((
        1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
        / math.pi) / 2.0 * n)
    tile_coords = namedtuple('TileCoords', 'x,y')
    return tile_coords(x=xtile, y=ytile)

def num2deg(xtile, ytile, zoom):
    """Convert tile number to coordinates (of the upper corner)"""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return mapnik.Coord(y=lat_deg, x=lon_deg)



# ============================================================
#                        TILE RENDERER
# ============================================================

class TiledMapRenderer(object):
    """ Mapnik Slippy Map - Tile Renderer 
    """
    def __init__(self, mapobj):
        self.m = mapobj
        self.GOOGLEMERC = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
              '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
        self.DATA_PROJECTION = mapnik.Projection(GOOGLEMERC)
        self.TILE_WIDTH = 256
        self.TILE_HEIGHT = 256

    def deg2num(self, lat_deg, lon_deg, zoom):
        """Convert coordinates to tile number"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((
            1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
            / math.pi) / 2.0 * n)
        tile_coords = namedtuple('TileCoords', 'x,y')
        return tile_coords(x=xtile, y=ytile)

    def num2deg(self, xtile, ytile, zoom):
        """Convert tile number to coordinates (of the upper corner)"""
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return mapnik.Coord(y=lat_deg, x=lon_deg)

    def render_tile(self, z, x, y):
        """
        renders map tile
            :param z: Zoom level
            :param x: Tile horizontal position
            :param y: Tile vertical position
        """
        # Set Tile Bounds
        topleft = self.num2deg(x, y, z)
        bottomright = self.num2deg(x + 1, y + 1, z)
        # Bounding box for the tile
        bbox = mapnik.Box2d(topleft, bottomright)
        bbox = self.DATA_PROJECTION.forward(bbox)
        # Zoom to bounding box
        self.m.zoom_to_box(bbox)
        # Set buffer
        MIN_BUFFER = 256
        self.m.buffer_size = max(self.m.buffer_size, MIN_BUFFER)
        # Render image with default Agg renderer
        im = mapnik.Image(TILE_WIDTH, TILE_WIDTH)
        mapnik.render(self.m, im)
        # Return image
        return im



# ============================================================
#                        BASEMAP TILES
# ============================================================

@app.route('/tms')
def root():
    # if not app.config['MASTERKEY'] == request.args.get('apikey'):
        # raise ValueError("Unauthorized")
    baseURL = get_ip() + '/tms'
    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8" ?>')
    xml.append('<Services>')
    xml.append(' <TileMapService title="Georeferenced Blueprint Tile Map Service" version="1.0" href="' + baseURL + '/1.0"/>')
    xml.append(' <TileMapService title="Upload Image Tile Map Service" version="2.0" href="' + baseURL + '/2.0"/>')
    xml.append('</Services>')
    return Response(xml,mimetype='text/xml') 

@app.route('/tms/1.0')
def service():
    # if not app.config['MASTERKEY'] == request.args.get('apikey'):
        # raise ValueError("Unauthorized")
    baseURL = get_ip() + '/tms/1.0'
    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8" ?>')
    xml.append('<TileMapService version="1.0" services="' + baseURL + '">')
    xml.append(' <Title>Find Tile Map Service</Title>')
    xml.append(' <Abstract></Abstract>')
    xml.append(' <TileMaps>')
    directory = os.path.join("baselayers","*.xml")
    baselayers = glob.glob(directory)
    for baselayer in baselayers:
        layer = os.path.basename(baselayer)
        xml.append('<TileMap title="' + layer + '" srs="EPSG:4326" href="' + baseURL + '/' + layer + '"/>')
    xml.append(' </TileMaps>')
    xml.append('</TileMapService>')
    return Response(xml,mimetype='text/xml') 

@app.route('/tms/1.0/<layer>')
def tileMap(layer):
    # if not app.config['MASTERKEY'] == request.args.get('apikey'):
        # raise ValueError("Unauthorized")
    folder = os.path.join("baselayers",layer)
    if not os.path.exists(folder):
        raise ValueError("files not found")
    baseURL = get_ip() + '/tms/1.0/' + layer
    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8" ?>')
    xml.append('<TileMap version="1.0" tilemapservice="' + baseURL + '">')
    xml.append(' <Title>' + layer + '</Title>')
    xml.append(' <Abstract></Abstract>')
    xml.append(' <SRS>EPSG:4326</SRS>')
    xml.append(' <BoundingBox minx="-180" miny="-90" maxx="180" maxy="90"/>')
    xml.append(' <Origin x="-180" y="-90"/>')
    xml.append(' <TileFormat width="' + str(TILE_WIDTH) + '" height="' + str(TILE_HEIGHT) + '" ' + 'mime-type="image/png" extension="png"/>')
    xml.append(' <TileSets profile="global-geodetic">')
    for zoomLevel in range(0, MAX_ZOOM_LEVEL+1):
        unitsPerPixel = _unitsPerPixel(zoomLevel)
        xml.append('<TileSet href="' + baseURL + '/' + str(zoomLevel) + '" units-per-pixel="'+str(unitsPerPixel) + '" order="' + str(zoomLevel) + '"/>')
    xml.append(' </TileSets>')
    xml.append('</TileMap>')
    return Response(xml,mimetype='text/xml') 

@app.route('/tms/1.0/<layer>/<int:z>/<int:x>/<int:y>.png')
def render_tile(layer, z, x, y):
    """
    Render the tile using mapnik.
    """
    folder = os.path.join("baselayers",layer)
    if not os.path.exists(folder):
        raise ValueError("files not found")
    # Create map
    m = mapnik.Map(TILE_WIDTH, TILE_HEIGHT)
    # Load mapnik xml stylesheet
    stylesheet = os.path.join("baselayers",str(layer),"style.xml")
    mapnik.load_map(m, stylesheet)
    # Zoom to all features
    m.zoom_all()
    # Store artifacts
    stylesheet = os.path.join("stylesheets",layer + ".xml")
    mapnik.save_map(m, str(stylesheet))
    # Render Map Tile
    renderer = TiledMapRenderer(m)
    im = renderer.render_tile(z, x, y)
    # Return image
    return im.tostring('png'), 200, {'Content-type': 'image/png'}



# ============================================================
#                        UPLOAD TILES
# ============================================================

def get_rasters():
    folder = os.path.join("baselayers")
    files = glob.glob(folder + "/*.tif")
    results = []
    for file in files:
        file = os.path.basename(file)
        file = file.replace(".tif","")
        results.append(file)
    return results

@app.route('/tms/2.0')
def rasters_service():
    # if not app.config['MASTERKEY'] == request.args.get('apikey'):
        # raise ValueError("Unauthorized")
    baseURL = get_ip() + '/tms/2.0'
    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8" ?>')
    xml.append('<TileMapService version="2.0" services="' + baseURL + '">')
    xml.append(' <Title>Find Tile Map Service</Title>')
    xml.append(' <Abstract></Abstract>')
    xml.append(' <TileMaps>')
    for baselayer in get_rasters():
        layer = os.path.basename(baselayer)
        xml.append('<TileMap title="' + layer + '" srs="EPSG:4326" href="' + baseURL + '/' + layer + '"/>')
    xml.append(' </TileMaps>')
    xml.append('</TileMapService>')
    return Response(xml,mimetype='text/xml') 

@app.route('/tms/2.0/<layer>')
def rasters_tileMap(layer):
    # if not app.config['MASTERKEY'] == request.args.get('apikey'):
        # raise ValueError("Unauthorized")
    file = os.path.join("baselayers", layer + ".tif")
    if not os.path.exists(file):
        raise ValueError("file not found")
    baseURL = get_ip() + '/tms/2.0/' + layer
    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8" ?>')
    xml.append('<TileMap version="2.0" tilemapservice="' + baseURL + '">')
    xml.append(' <Title>' + layer + '</Title>')
    xml.append(' <Abstract></Abstract>')
    xml.append(' <SRS>EPSG:4326</SRS>')
    xml.append(' <BoundingBox minx="-180" miny="-90" maxx="180" maxy="90"/>')
    xml.append(' <Origin x="-180" y="-90"/>')
    xml.append(' <TileFormat width="' + str(TILE_WIDTH) + '" height="' + str(TILE_HEIGHT) + '" ' + 'mime-type="image/png" extension="png"/>')
    xml.append(' <TileSets profile="global-geodetic">')
    for zoomLevel in range(0, MAX_ZOOM_LEVEL+1):
        unitsPerPixel = _unitsPerPixel(zoomLevel)
        xml.append('<TileSet href="' + baseURL + '/' + str(zoomLevel) + '" units-per-pixel="'+str(unitsPerPixel) + '" order="' + str(zoomLevel) + '"/>')
    xml.append(' </TileSets>')
    xml.append('</TileMap>')
    return Response(xml,mimetype='text/xml') 

@app.route('/tms/2.0/<datasource>/<int:z>/<int:x>/<int:y>.png')
def render_raster_tile(datasource, z, x, y):
    file = os.path.join("baselayers", datasource + ".tif")
    if not os.path.exists(file):
        raise ValueError("file not found")
    raster = mapnik.Gdal(file=os.path.abspath(file))
    lyr = mapnik.Layer("TIFF")
    lyr.datasource = raster
    lyr.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
    # Create map
    m = mapnik.Map(TILE_WIDTH, TILE_HEIGHT)
    # Create Style and Rules
    s = mapnik.Style()
    r = mapnik.Rule()
    # Create style for lyr
    r.symbols.append(mapnik.RasterSymbolizer())
    s.rules.append(r)
    m.append_style('TIFF',s)
    lyr.styles.append('TIFF')
    # Set map srs to google
    # merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
    # m.srs = merc.params()
    m.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
    # Add layer to map
    m.layers.append(lyr)
    # Zoom to all features
    #m.maximum_extent = mapnik.Box2d(-180,-90,180,90)
    m.maximum_extent = mapnik.Box2d(-20037508.34,-20037508.34,20037508.34,20037508.34) # merc_bounds
    m.zoom_all()
    # Store artifacts
    stylesheet = os.path.join("stylesheets", datasource + ".xml")
    mapnik.save_map(m, str(stylesheet))
    # Render Map Tile
    renderer = TiledMapRenderer(m)
    im = renderer.render_tile(z, x, y)
    # Return image
    return im.tostring('png'), 200, {'Content-type': 'image/png'}



# ============================================================
#                        IMAGE UPLOADS
# ============================================================

def resize_canvas(old_image_path="314.jpg", new_image_path="temp_file.jpg",
                  canvas_width=500, canvas_height=500):
    """Resize the canvas of old_image_path and store the new image in
       new_image_path. Center the image on the new canvas.
    """
    #im = Image.open(old_image_path)
    im = old_image_path
    old_width, old_height = im.size

    # Center the image
    x1 = int(math.floor((canvas_width - old_width) / 2))
    y1 = int(math.floor((canvas_height - old_height) / 2))

    mode = im.mode
    if len(mode) == 1:  # L, 1
        new_background = (255)
    if len(mode) == 3:  # RGB
        new_background = (255, 255, 255)
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (255, 255, 255, 255)

    newImage = Image.new(mode, (canvas_width, canvas_height), new_background)
    newImage.paste(im, (x1, y1, x1 + old_width, y1 + old_height))
    #newImage.save(new_image_path)

    #return new_image_path
    return newImage

def create_baselayer_from_image(filename):
    """ Creates .tiff from uploaded file """
    # file_path = os.path.join("uploads",filename)
    # img = file_path
    # im = Image.open(file_path)
    img = Image.open(filename)
    #width, height = im.size
    width, height = img.size
    if width != height:
        dim = [width,height]
        dim.sort()
        # Resize canvas so image is square
        img = resize_canvas(
                old_image_path=img,
                canvas_height=dim[-1],
                canvas_width=dim[-1],
                new_image_path=os.path.join("uploads",str(time.time()) + ".png")
            )
    basename = str(generate_uuid())
    img_file = os.path.join("uploads",basename + ".png")
    img.save(img_file)
    tiff_file = os.path.join("rasters", basename + ".tiff")
    subprocess.Popen([
            "gdal_translate",
            "-of",
            "Gtiff",
            "-a_ullr",
            "-20037508.34",
            "20037508.34",
            "20037508.34",
            "-20037508.34",
            "-a_srs",
            "EPSG:4326",
            os.path.abspath(img_file),
            os.path.abspath(tiff_file)
        ])
    return os.path.basename(tiff_file).replace(".tiff","")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not app.config['MASTERKEY'] == request.args.get('apikey'):
        raise ValueError("Unauthorized")
    UPLOAD_FOLDER = os.path.join('uploads')
    message = ''
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # new_baselayer = create_baselayer_from_image(str(time.time()) + "_" + filename)
            # file.save(os.path.join(UPLOAD_FOLDER, str(time.time()) + "_" + filename))
            new_baselayer = create_baselayer_from_image(file)
            message = "/tms/2.0/" + new_baselayer + "/{z}/{x}/{y}.png"
    return '''
        <!doctype html>
        <title>Create baselayer</title>
        <h2>Create Baselayer</h2>
        <h3>Upload File</h3>
        <form action="" method=post enctype=multipart/form-data>
            <p>
                <input type=file name=file>
                <input type=submit value=Upload>
            </p>
        </form>
        <p>
            %s
        </p>
    ''' % message



# ============================================================
#                         Run Server                          
# ============================================================

if __name__ == '__main__':
    app.run(
        host= '0.0.0.0',
        port=5000
    )





'''

prep jpg or png file
gdal_translate -of Gtiff -a_ullr -20037508.34 20037508.34 20037508.34 -20037508.34 -a_srs EPSG:4326 TEST.jpg TEST.tiff 

L.tileLayer("/tms/2.0/TEST4326M/{z}/{x}/{y}.png",{}).addTo(map)

'''

