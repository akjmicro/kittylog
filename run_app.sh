#!/bin/bash

# kill any previous
pkill -KILL -f flask

# rerun
FLASK_APP=kittylog/app.py python3 -m flask run --host=0.0.0.0 > app.log 2>&1 &
