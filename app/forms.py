from flask.ext.wtf import Form
from app.models import User
from wtforms import TextField, BooleanField, SubmitField, PasswordField, FileField
from wtforms.validators import Required, EqualTo, DataRequired, Length

class LoginForm(Form):
    username = TextField('Username', [Required(), Length(min=3, max=15)])
    password = PasswordField('Password', [Required(), Length(min=5, max=20)])
    remember_me = BooleanField('remember_me', default = False)

class RegisterForm(Form):
	username = TextField("Team Name", [Required("Username Field Required"), Length(min=3, max=15)])
	password = PasswordField('New Password', [Required("Password Field Required"), Length(min=5, max=20), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
