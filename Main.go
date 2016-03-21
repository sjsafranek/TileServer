package main

import (
	"log"
	"net/http"
)

func main() {

	router := NewRouter()

	log.Fatal(http.ListenAndServe("0.0.0.0:8080", router))
	//ListenAndServeTLS("0.0.0.0:8080", "myCertFile.pem", "myKeyFile.pem", router) error  FOR HTTPS

}
