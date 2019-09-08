#!/bin/bash

# kill any previous
pkill -KILL -f gunicorn

# run a gunicorn instance to serve the app:
source bin/activate
gunicorn -w 4 -b unix:kittylog.sock kittylog.wsgi:app > app.log 2>&1 &
