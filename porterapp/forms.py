__author__ = 'johnedenfield'


from flask_wtf import Form
from wtforms import StringField,SelectField, PasswordField, validators, SubmitField, HiddenField


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(message='A password is required'),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Register")

class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired("Please enter your Email.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Login")


class RateBeerForm(Form):
    rating =SelectField('Rating', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    beerid = HiddenField('BeerID')
    submit = SubmitField("Rate")

class DeleteRatingForm(Form):
    id = HiddenField('ID')
    url = HiddenField('Url')
