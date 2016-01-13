# Tile Server
This application will serve MBTiles from a file named tiles.mbtiles. The route is http://localhost:8080/dbname/z/x/y

The HTML is a leaflet map that that loads tiles from http://localhost:8080/tiles/{z}/{x}/{y}

This project can be modified to server multiple tile layer if you copy the handler and assign it to another route making some small changes (dbname for starters). 

The structure of the server was taken from [Making a RESTful JSON API in Go](http://thenewstack.io/make-a-restful-json-api-go/)

The tileserver was built as a copy of the PHP version by [Bryan McBride](https://github.com/bmcbride/PHP-MBTiles-Server)

