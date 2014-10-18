from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.forms import LoginForm, RegisterForm, UploadForm
from app.models import User, ROLE_USER, ROLE_ADMIN, UserFile
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SOLUTION_TESTS_FOLDER
from datetime import datetime
from werkzeug import secure_filename
import os, subprocess, time, threading, errno

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

@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    user = g.user

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
def allowed_file(file_name):
    return '.' in file_name and file_name.split('.')[-1] in ALLOWED_EXTENSIONS

@app.route('/upload/<problem_num>', methods = ['GET', 'POST'])
@login_required
def upload(problem_num):
    user = g.user
    form = UploadForm()
    if form.validate_on_submit():
        file_data = form.upload.data
        file_name = secure_filename(file_data.filename)
        if file_data and allowed_file(file_name):

            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                "Teams",
                user.username,
                file_name
            )
            #file_size = os.path.getsize(file_data)
            # maybe this : if file_size < MAX_CONTENT_LENGTH
            # tries to remove the file if it exists before creating a new one
            if not os.path.isfile(file_path):
                form.upload.data.save(file_path)
                flash("File " + file_name + " uploaded successfully!")

                # changes file status
                user.files[int(problem_num)-1].status = "Submitted"
                db.session.commit()

                # THIS SHIT IS SUPER IMPORTANT!!!!!
                if grade_submission(user, file_path, file_name, problem_num):
                    update_file_status(user, problem_num, "Solved")
                    update_score(user, int(problem_num))
                else:
                    update_file_status(user, problem_num, "Failed")
                    os.remove(file_path)

                return redirect(url_for('index'))
            else:
                flash("Your submission is waiting to be graded. Please wait until you receive feedback to submit again.")
        else:
            flash("Please choose a file with extension '.cs', '.java', '.cpp', or '.py'")
    return render_template(problem_num+'.html', title = "Problem "+problem_num, form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def update_file_status(user, problem_num, new_status):
    file_to_update = user.files[int(problem_num)-1]
    file_to_update.status = new_status
    db.session.commit()

def update_score(user, problem_num):
    if problem_num in range(0,10):
        user.score += 10
    elif problem_num in range(10,20):
        user.score += 20
    else:
        user.score += 30
    db.session.commit()

def grade_submission(user, file_path, file_name, problem_num):
    test_input_path = os.path.join(
        app.config['SOLUTION_TESTS_FOLDER'],
        'input_'+str(problem_num)+'.txt'
    )
    test_output_path = os.path.join(
        app.config['SOLUTION_TESTS_FOLDER'],
        'output_'+str(problem_num)+'.txt'
    )
    user_output_file_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        'grading_folder',
        user.username+'_'+str(problem_num)+'_'+'output.txt'
    )

    test_input = open(test_input_path, 'r')
    test_output = open(test_output_path, 'r')
    user_file_output = open(user_output_file_path, 'w+')

    file_ext = file_name.split('.')[1] # get the file extension
    exec_name = file_name.split('.')[0]

    if file_ext == 'cpp':
        pre = subprocess.Popen(['g++', file_path, '-o', exec_name])
        pre.wait()

        p = subprocess.Popen(
            ['./'+exec_name],
            stdin=test_input, 
            stdout=user_file_output
        )

    elif file_ext == 'java':
        pre = subprocess.Popen(['javac', file_path])
        pre.wait()

        p = subprocess.Popen(
            ['java', exec_name],
            stdin=test_input, 
            stdout=user_file_output
        )

    elif file_ext == 'py':

        p = subprocess.Popen(
            ['python', file_path],
            stdin=test_input, 
            stdout=user_file_output
        )
    elif file_ext == 'cs':
        pre = subprocess.Popen(['mcs', file_name])
        pre.wait()

        p = subprocess.Popen(
            ['mono', exec_name+'.exe'],
            stdin=test_input, 
            stdout=user_file_output
        )

    t = threading.Timer(60.0, timeout, [p] )
    t.start()
    #p.join()
    p.wait()
    t.cancel()
    user_file_output.flush()
    user_file_output.seek(0,0)

    return checkAns(user_file_output.readlines(), test_output.readlines())


def checkAns(user_file_output, test_output):
    for l, line in enumerate(user_file_output):
        if test_output[l] != line:
            return False
    return True

def timeout(p):
    if p.poll() is None:
        try:
            p.kill()
            print('Error: process taking too long to complete--terminating')
        except OSError as e:
            if e.errno != errno.ESRCH:
                raise