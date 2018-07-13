#!/usr/bin/env python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


from app import views, models
