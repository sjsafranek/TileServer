#!/bin/bash

export GOPATH="`pwd`"

key="$1"

case $key in
    -i|--install)
        echo "checking requirements..."
        if [ ! -d "`pwd`/src/github.com/gorilla/mux" ]; then
            echo "installing mux..."
            go get github.com/gorilla/mux
        fi

        if [ ! -d "`pwd`/src/github.com/mattn/go-sqlite3" ]; then
            echo "installing bolt..."
            go get github.com/mattn/go-sqlite3
        fi

        echo "done!"
    ;;
    -r| --run)
        go run *.go    
    ;;
    -h| --help)
        echo "-c -t -h -r"     
    ;;
    *)
        echo "unknown option"
    ;;
esac
