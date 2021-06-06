from flask import Flask
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(basedir, 'test.db'),
    )

from app import routes