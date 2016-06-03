package main

import (
	"flag"
	"log"
	"net/http"
	// "tileserver/lib"
)

var (
	port string
)

func init() {
	// flag.Usage = func() {
	// 	fmt.Println("Usage: mbtile_builder [method] [option]\n")
	// 	fmt.Printf("Methods:\n")
	// 	fmt.Printf("  install\n\tInstall requirements\n")
	// 	fmt.Printf("\n")
	// 	fmt.Printf("Defaults:\n")
	// 	flag.PrintDefaults()
	// }
	flag.StringVar(&port, "port", "8888", "server [port")
	flag.Parse()
}

func main() {

	router := NewRouter()

	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, router))
	//ListenAndServeTLS("0.0.0.0:8080", "myCertFile.pem", "myKeyFile.pem", router) error  FOR HTTPS

}
