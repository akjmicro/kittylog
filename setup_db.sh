#!/bin/bash

if [ ! -f kittylog/kittylog.db ]; then
    echo "Creating the initial sqlite3 database"
    sqlite3 kittylog/kittylog.db \
        "CREATE TABLE IF NOT EXISTS food ("
            "timestamp text, feeder text, kitty text, wet text, dry text, "
            "hairball text, treats text);"
        "CREATE TABLE IF NOT EXISTS water (timestamp text, feeder text);"
        "CREATE INDEX IF NOT EXISTS kittylog_index ON food (timestamp);"
        "CREATE INDEX IF NOT EXISTS water_index ON water (timestamp);"
fi
