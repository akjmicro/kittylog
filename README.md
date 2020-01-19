# kittylog
A way to keep track of your kitty's diet(s) as you feed them through the
day. Designed to be run on your private LAN (your wifi router in your house.
At our place, we serve this via a Rasperry Pi 3.

# Quick start
* install `python3` and `flask`
* `python3 setup.py develop`
* change the names of your cats and humans to reflect your household in the `config.yml` file
* From the code root directory: `chmod 777 setup_db.sh run_app.sh`
* Run the db setup script: `./setup_db.sh`
* From the kittlog directory: `./run_app.sh` or, if necessary: `sudo ./run_app.sh`
* Go to the IP of the server on your local network, and see the app, e.g. enter `ip_of_host:5000` into your browser URL bar
* If so inclined, you can set up `nginx` to proxy-serve standard `port 80` requests to your server to the `flask` 'kittylog' process. It's really overkill, though.

# TODO:
* dynamic creation of statistics, driven from YAML config.
  ATM, the newer `stats` page is hard-coded for my cats, which isn't ideal.

That's it!

Email questions to akjmicro@gmail.com
