package main

// This file contains various demo applications of the go-mapnik package

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/sjsafranek/go-mapnik/mapnik"
	"github.com/sjsafranek/go-mapnik/maptiles"
)

// Render a simple map of europe to a PNG file
func SimpleExample(map_file string) {
	m := mapnik.NewMap(1600, 1200)
	defer m.Free()
	m.Load(map_file)
	fmt.Println(m.SRS())
	// Perform a projection that is only neccessary because stylesheet.xml
	// is using EPSG:3857 rather than WGS84
	p := m.Projection()
	ll := p.Forward(mapnik.Coord{0, 35})  // 0 degrees longitude, 35 degrees north
	ur := p.Forward(mapnik.Coord{16, 70}) // 16 degrees east, 70 degrees north
	m.ZoomToMinMax(ll.X, ll.Y, ur.X, ur.Y)
	blob, err := m.RenderToMemoryPng()
	if err != nil {
		fmt.Println(err)
		return
	}
	ioutil.WriteFile("mapnik.png", blob, 0644)
}

// Serve a single stylesheet via HTTP. Open view_tileserver.html in your browser
// to see the results.
// The created tiles are cached in an sqlite database (MBTiles 1.2 conform) so
// successive access a tile is much faster.
func TileserverWithCaching(map_file string) {
	cache := "gomapnikcache.sqlite"
	os.Remove(cache)
	t := maptiles.NewTileServer(cache)
	t.AddMapnikLayer("default", map_file)
	http.ListenAndServe(":8080", t)
}

// Before uncommenting the GenerateOSMTiles call make sure you have
// the neccessary OSM sources. Consult OSM wiki for details.
func main() {
	// SimpleExample()
	//GenerateOSMTiles()
	TileserverWithCaching("sampledata/stylesheet.xml")
}


/*

https://github.com/sjsafranek/go-mapnik

apt-get install libmapnik-dev

export GOPATH="`pwd`"
go get -d github.com/sjsafranek/go-mapnik/mapnik

cd src/github.com/sjsafranek/go-mapnik/mapnik/
./configure.bash
cd ../../../../..


*/