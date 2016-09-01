package main

import (
	"flag"
	"log"
	"net/http"
)

var (
	port string
)

func init() {
	flag.StringVar(&port, "p", "8888", "server [port]")
	flag.Parse()
}

func main() {
	router := NewRouter()
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, router))
}
