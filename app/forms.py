from flask.ext.wtf import Form
from app.models import User
from wtforms import TextField, BooleanField, TextField, TextAreaField, SubmitField, ValidationError, PasswordField
from wtforms.validators import Required, EqualTo

class LoginForm(Form):
    username = TextField('Username', [Required()])
    password = TextField('Password', [Required()])
    remember_me = BooleanField('remember_me', default = False)

class RegisterForm(Form):
	username = TextField("First name",  [Required("Enter your desired username.")])
	password = PasswordField('New Password', [Required(), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	submit = SubmitField("Create account")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
	
	def validate(self):
		if not Form.validate(self):
			return False
		user = User.query.filter_by(username = self.username.data).first()
		if user:
			self.username.errors.append("That username is already taken")
			return False
		else:
			return True
