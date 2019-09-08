#!/bin/bash

if [ ! -f kittylog/kittylog.db ]; then
    echo "Creating the initial sqlite3 database"
    sqlite3 kittylog/kittylog.db \
        "CREATE TABLE food ("
            "timestamp text,"
            "human text, kitty text,"
            "wet text, dry text,"
            "hairball text, regular text);"
        "CREATE TABLE water (timestamp text, human text);"
fi
