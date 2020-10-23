import logging
import yaml

from flask import Flask

config = yaml.safe_load(open("config.yml"))

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "aardvark67d441f2b-stellar_6176a41f275lunatic"
app.logger.setLevel(logging.DEBUG)
