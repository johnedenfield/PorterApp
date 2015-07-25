__author__ = 'johnedenfield'

from flask import Flask


app = Flask(__name__)
app.config.from_pyfile('config.py')

print  app.config['SQLALCHEMY_DATABASE_URI']

import views,forms, models
