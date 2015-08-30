__author__ = 'johnedenfield'

from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
app.config.from_pyfile('config.py')

import models, forms, views
