#!/bin/bash

if [ ! -f kittylog/kittylog.db ]; then
    echo "Creating the initial sqlite3 database"
    sqlite3 kittylog/kittylog.db \
        "CREATE TABLE kittylog(timestamp text, feeder text, kitty text, 
            wet text, dry text, hairball text, treats text);"
fi
