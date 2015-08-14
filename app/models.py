__author__ = 'johnedenfield'

from datetime import datetime
from . import app  # Import app from init
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import urllib

db = SQLAlchemy(app)

# Database Schema


class UserBeerList(db.Model):
    __tablename__ = 'UserBeerList'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DateAndTime = db.Column(db.DateTime)
    User_ID = db.Column(db.Integer, db.ForeignKey('User.ID'))
    Beer_ID = db.Column(db.Integer, db.ForeignKey('DraftList.Beer_ID'))
    Rating = db.Column(db.Integer)

    # Relationships
    UserInfo = db.relationship("User", foreign_keys=[User_ID])
    BeerInfo = db.relationship("DraftList", foreign_keys=[Beer_ID])

    def __init__(self, User_ID, Beer_ID, Rating, DateAndTime=None):
        if DateAndTime is None:
            self.DateAndTime = datetime.utcnow()

        self.User_ID = User_ID
        self.Beer_ID = Beer_ID
        self.Rating = Rating


class DraftList(db.Model):
    __tablename__ = 'DraftList'

    Beer_ID = db.Column(db.String, primary_key=True, autoincrement=False)
    OnDraft = db.Column(db.Integer)
    Updated = db.Column(db.DateTime)
    Brewery = db.Column(db.String)
    Beer = db.Column(db.String)
    Style = db.Column(db.String)
    Origin = db.Column(db.String)
    Volume = db.Column(db.String)
    ABV = db.Column(db.String)
    Description = db.Column(db.String)
    BeerRating = db.Column(db.Float)
    RatingSite = db.Column(db.String)
    NotifyUser = db.Column(db.Integer)

    def set_RatingSite(self, url):
        self.RatingSite = urllib.quote_plus(url)

    def get_RatingSite(self):
        return urllib.unquote_plus(self.RatingSite)


class DraftHistory(db.Model):
    __tablename__ = 'DraftHistory'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DateAndTime = db.Column(db.DateTime)
    Beer_ID = db.Column(db.String, db.ForeignKey('DraftList.Beer_ID'))

    BeerInfo = db.relationship("DraftList", foreign_keys=[Beer_ID])


# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'User'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String)
    UserName = db.Column(db.String)
    Pwdhash = db.Column(db.String)

    def __init__(self, UserName, Email, Password):
        self.UserName = UserName
        self.Email = Email.lower()
        self.set_password(Password)

    def set_password(self, password):
        self.Pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Pwdhash, password)

    def get_id(self):
        return unicode(self.ID)
