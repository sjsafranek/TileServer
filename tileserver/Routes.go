package main

import "net/http"

type Route struct {
	Name        string
	Method      string
	Pattern     string
	HandlerFunc http.HandlerFunc
}

type Routes []Route

var routes = Routes{

	Route{
		"Tiles",
		"GET",
		"/{db}/{z}/{x}/{y}",
		Tiles,
	},

	Route{
		"MetaData",
		"GET",
		"/metadata/{db}",
		MetaDataHandler,
	},


	Route{
		"Map",
		"GET",
		"/map/{db}",
		MapHandler,
	},

}
