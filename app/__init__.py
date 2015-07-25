__author__ = 'johnedenfield'

from flask import Flask


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


import views,forms, models
