from flask.ext.wtf import Form, RecaptchaField
from app.models import User
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextField, BooleanField, SubmitField, PasswordField
from wtforms.validators import Required, EqualTo, DataRequired, Length

class LoginForm(Form):
    username = TextField('Username', validators = [DataRequired(), Length(min=3, max=15)])
    password = PasswordField('Password', validators = [DataRequired(), Length(min=5, max=20)])
    remember_me = BooleanField('remember_me', default = False)

class RegisterForm(Form):
	username = TextField("Team Name", validators = [DataRequired("Username Field Required"), Length(min=3, max=15)])
	password = PasswordField('New Password', validators = [DataRequired("Password Field Required"), Length(min=5, max=20), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	recaptcha = RecaptchaField()

class UploadForm(Form):
	upload = FileField("Upload your solution:", validators = [DataRequired("Please choose a file to submit!")])
	recaptcha = RecaptchaField()

class EditUserScoreForm(Form):
	teamname = TextField("Team Name", validators = [DataRequired()])
	problem_number = TextField("Problem Number", validators = [DataRequired()])
	status = TextField("Updated Status", validators = [DataRequired()])
