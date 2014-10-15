from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.forms import LoginForm, RegisterForm, UploadForm
from app.models import User, ROLE_USER, ROLE_ADMIN, UserFile
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from datetime import datetime
from werkzeug import secure_filename
import os
import errno

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# sets current user from flask-login to g.user
@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

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
            directory = os.path.join(app.config['UPLOAD_FOLDER'], 'Teams', form.username.data)
            if not os.path.exists(directory):
                os.makedirs(directory) 

            db.session.add(user)

            # creates UserFile objects to represent team submissions
            for i in range(30):
                user_file = UserFile(
                    problem_number=i+1, 
                    status="Not Submitted",
                    timestamp = datetime.utcnow(), 
                    team = user)
                db.session.add(user_file)

            db.session.commit()

            flash('User successfully registered')
            return redirect(url_for('login'))
        else:
            form.username.errors.append('That username is already taken!')
    return render_template('register.html', form = form)

def update_score(user):
    # looks at team folder files to check if there are any new
    directory = os.path.join(app.config['UPLOAD_FOLDER'], 'Teams', user.username)
    # loops through each file in the directory
    for p_sol in os.listdir(directory):

        prob_num = int(p_sol.split('.')[0].split('_')[1])
        file_to_update = user.files[prob_num-1]

        if file_to_update.status == "Submitted":
            file_to_update.status = "Solved"
            if prob_num in range(1,11):
                user.score += 10
            elif prob_num in range(11,21):
                user.score += 20
            else:
                user.score += 30

    db.session.commit()

@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    user = g.user
    update_score(user)

    return render_template("index.html",
        title = user.username,
        score = user.score,
        user = user,
        challenges = user.files)

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
        registered_user = User.query.filter_by(username=username).first()
        if registered_user is not None:
            if registered_user.check_password(password):
                remember_me = False
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)
                login_user(registered_user, remember = remember_me)
                flash('Logged in successfully')
                return redirect(request.args.get('next') or url_for('index'))
            else:
                form.password.errors.append("Invalid password!")
        else:
            form.username.errors.append("Invalid username!")
    return render_template('login.html', title = 'Sign In', form = form)

# checks if file is of proper type
def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1] in ALLOWED_EXTENSIONS

@app.route('/upload/<problem_num>', methods = ['GET', 'POST'])
@login_required
def upload(problem_num):
    user = g.user
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.upload.data.filename)
        if form.upload.data and allowed_file(filename):

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                'grading_queue',
                user.username+"_"+problem_num+filename[filename.rfind('.'):])

            # tries to remove the file if it exists before creating a new one
            if not os.path.isfile(filepath):
                form.upload.data.save(filepath)
                flash("File " + filename + " uploaded successfully!")

                # changes file status
                user.files[int(problem_num)-1].status = "Submitted"
                db.session.commit()

                return redirect(url_for('index'))
            else:
                flash("Your submission is waiting to be graded. Please wait until you receive feedback to submit again.")
        else:
            flash("Please choose a file with extension '.cs', '.java', '.cpp', or '.py'")
    return render_template(problem_num+'.html', title = "Problem "+problem_num, form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))