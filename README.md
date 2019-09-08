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
* Set up `nginx` to serve local apps from port 80 and redirect to the
  `kittylog` process. E.G., in `/etc/nginx/sites-enabled`:
  ```
  server {
    listen 80;
    server_name 192.168.1.70;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/pi/kittylog/kittylog.sock;
    }
  }
  ```
  and then:
  ```
  sudo ln -s /etc/nginx/sites-available/kittylog /etc/nginx/sites-enabled
  sudo service restart nginx
  ```
* From the kittlog directory: `sudo ./run_app.sh`
* Go to the IP of the server on your local network, and see the app, e.g. enter `ip_of_host:80` into your browser URL bar

That's it!

Email questions to akjmicro@gmail.com
