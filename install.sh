#!/bin/bash

export GOPATH="`pwd`"

echo "creating workspace..."

# Create required directories
echo "creating directories..."
if [ ! -d "`pwd`/bin" ]; then
    mkdir bin
fi

if [ ! -d "`pwd`/src" ]; then
    mkdir src
    mkdir src/tileserver
fi

# Copy source files
echo "copying source files..."
cp -R tileserver/* src/tileserver/


# Download required libraries
echo "checking requirements..."

if [ ! -d "`pwd`/src/github.com/gorilla/mux" ]; then
    echo "downloading gorilla mux..."
    go get github.com/gorilla/mux
fi

if [ ! -d "`pwd`/src/github.com/mattn/go-sqlite3" ]; then
    echo "downloading go-sqlite3..."
    go get github.com/mattn/go-sqlite3
fi

echo "done!"
