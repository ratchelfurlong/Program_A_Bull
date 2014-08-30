from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.forms import LoginForm, RegisterForm
from app.models import User, ROLE_USER, ROLE_ADMIN
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from werkzeug import secure_filename
import os
import errno

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# checks if file is of proper type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# sets current user from flask-login to g.user
@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/register' , methods=['GET','POST'])
def register():
    # if user is logged in, redirect them to index
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegisterForm()
    # tries to register user
    if form.validate_on_submit():
        new_user = User.query.filter_by(username=form.username.data).first()
        if new_user is None:
            user = User(form.username.data, form.password.data)

            # makes directory to store files on 
            directory = os.path.join(app.config['UPLOAD_FOLDER'], form.username.data)
            if not os.path.exists(directory):
                os.makedirs(directory) 

            db.session.add(user)
            db.session.commit()
            flash('User successfully registered')
            return redirect(url_for('login'))
        else:
            form.username.errors.append('That username is already taken!')
    return render_template('register.html', form = form)


@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    user = g.user
    return render_template("index.html",
        title = user.username,
        user = user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    # if user is logged in, redirect them to index
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    # tries to login user
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        session['remember_me'] = form.remember_me.data
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        registered_user = User.query.filter_by(username=username).first()
        if registered_user is not None:
            if registered_user.check_password(password):
                login_user(registered_user, remember = remember_me)
                flash('Logged in successfully')
                return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', title = 'Sign In', form = form)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    user = g.user
    if request.method == 'POST':
        submitted_file = request.files['file']
        if submitted_file and allowed_file(submitted_file.filename):
            filename = secure_filename(submitted_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.username, filename)
            # tries to remove the file if it exists before creating a new one
            try:
                os.remove(filepath)
            except OSError:
                pass
            submitted_file.save(filepath)
            flash("File " + filename + " uploaded successfully!")
            return redirect(url_for('index'))
        else:
            form.solution_file.errors.append("Please enter a valid file extension.")
            return redirect(url_for('index'))
    return render_template('upload.html', title = "Upload File")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))