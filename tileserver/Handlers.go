package main

import (
	"encoding/json"
	"database/sql"
	"net/http"
	"html/template"
	"fmt"
	"os"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

func Tiles(w http.ResponseWriter, r *http.Request) {
	// Set headers
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "image/png")

	// Get params
	vars := mux.Vars(r)
	dbname := vars["db"]
	z := vars["z"]
	x := vars["x"]
	y := vars["y"]

	// check for file
	if _, err := os.Stat(dbname+".mbtiles"); os.IsNotExist(err) {
		fmt.Println("File not found [" + dbname + ".mbtiles]")
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	// Open database
	db, _ := sql.Open("sqlite3", "./"+dbname+".mbtiles")
	rows, _ := db.Query("SELECT * FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?", z, x, y)

	for rows.Next() {

		var zoom_level int32
		var tile_column int32
		var tile_row int32
		var tile_data []byte
		rows.Scan(&zoom_level, &tile_column, &tile_row, &tile_data)

		w.Write(tile_data)
	}

	db.Close()

}

func MapHandler(w http.ResponseWriter, r *http.Request) {
	// Get params
	vars := mux.Vars(r)
	dbname := vars["db"]

	type MapData struct {
		DatabaseName string
		Version    string
	}

	// Return results
	map_tmpl := "./tmpl/map.html"
	tmpl, _ := template.ParseFiles(map_tmpl)
	tmpl.Execute(w, MapData{DatabaseName: dbname, Version: "1.0.0"})

}


func MetaDataHandler(w http.ResponseWriter, r *http.Request) {
	// Set headers
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	// Get params
	vars := mux.Vars(r)
	dbname := vars["db"]

	// check for file
	if _, err := os.Stat(dbname+".mbtiles"); os.IsNotExist(err) {
		fmt.Println("File not found [" + dbname + ".mbtiles]")
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	// Open database
	db, _ := sql.Open("sqlite3", "./"+dbname+".mbtiles")
	rows, _ := db.Query("SELECT * FROM metadata")

	metadata :=  make(map[string]string)

	for rows.Next() {

		var name string
		var value string
		rows.Scan(&name, &value)
		
		metadata[name] = value
	}

	db.Close()

	response_wrapper := make(map[string]interface{})
	response_wrapper["status"] = "success"
	response_wrapper["data"] = metadata

	js, err := json.Marshal(response_wrapper)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Write(js)

}


