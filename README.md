# kittylog
A way to keep track of your kitty's diet(s) as you feed them through the day. Designed to be run on your private LAN (your wifi router in your house. At our place, we serve this via a Rasperry Pi 3.

# Quick start
* install Python3 and flask
* `python3 setup.py develop`
* From the code root directory: `chmod 777 setup_db.sh run_app.sh`
* change the names of your cats and humans to reflect your household in the `ReusableForm` class
* `./run_app.sh`
* Go to the IP of the server on your local network, port 5000, and see the app, e.g. enter `192.168.1.43:5000` into your browser URL bar



