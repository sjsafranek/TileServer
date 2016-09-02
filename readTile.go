package main

import (
    "image"
    _ "image/jpeg" // Register JPEG format
    "image/png"    // Register PNG  format
    "image/color"
    "log"
    "os"
)

// Converted implements image.Image, so you can
// pretend that it is the converted image.
type Converted struct {
    Img image.Image
    Mod color.Model
}

// We return the new color model...
func (c *Converted) ColorModel() color.Model{
    return c.Mod
}

// ... but the original bounds
func (c *Converted) Bounds() image.Rectangle{
    return c.Img.Bounds()
}

// At forwards the call to the original image and
// then asks the color model to convert it.
func (c *Converted) At(x, y int) color.Color{
    return c.Mod.Convert(c.Img.At(x,y))
}

func main() {
    if len(os.Args) != 3 { log.Fatalln("Needs two arguments")}
    infile, err := os.Open(os.Args[1])
    if err != nil {
        log.Fatalln(err)
    }
    defer infile.Close()

    img, _, err := image.Decode(infile)
    if err != nil {
        log.Fatalln(err)
    }

    log.Println("Min X", img.Bounds().Min.X)
    log.Println("Min Y", img.Bounds().Min.Y)
    log.Println("Max X", img.Bounds().Max.X)
    log.Println("Max Y", img.Bounds().Max.Y)
    // for i := range(img.Bounds().Min.X, img.Bounds().Max.X) {
    for x := img.Bounds().Min.X; x < img.Bounds().Max.X; x++ {
        for y := img.Bounds().Min.Y; y < img.Bounds().Max.Y; y++ {
            log.Println("color", img.At(x, y))
        }
    }

    // Since Converted implements image, this is now a grayscale image
    gr := &Converted{img, color.GrayModel}
    // Or do something like this to convert it into a black and
    // white image.
    // bw := []color.Color{color.Black,color.White}
    // gr := &Converted{img, color.Palette(bw)}


    outfile, err := os.Create(os.Args[2])
    if err != nil {
        log.Fatalln(err)
    }
    defer outfile.Close()

    png.Encode(outfile,gr)
}



/*

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


*/