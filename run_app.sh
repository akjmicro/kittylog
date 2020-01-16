#!/bin/bash

source bin/activate

# kill previous
sudo pkill -KILL flask

# run it:
export FLASK_APP=wsgi.py
flask run  --host=0.0.0.0 >& app.log &
