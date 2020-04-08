#!/bin/bash

# kill any previous
pkill -KILL -f gunicorn

# run a gunicorn instance to serve the app:
source bin/activate
gunicorn -w 4 --bind localhost:5000 wsgi:app > app.log 2>&1 &
