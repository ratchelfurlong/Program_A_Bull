from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.forms import LoginForm, RegisterForm, UploadForm, EditUserScoreForm
from app.models import User, ROLE_USER, ROLE_ADMIN, UserFile
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SOLUTION_TESTS_FOLDER
from datetime import datetime
from werkzeug import secure_filename
import os, subprocess, time, threading, errno, shutil

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

@app.route('/upload/<problem_num>', methods = ['GET', 'POST'])
@login_required
def upload(problem_num):
    user = g.user
    form = UploadForm()
    if form.validate_on_submit():
        file_data = form.upload.data

        # renames file to username_prob_num.file_ext
        file_ext = file_data.filename.split('.')[1]
        file_name = secure_filename(user.username +"_"+problem_num+'.'+file_ext)

        if file_data and allowed_file(file_name):

            file_path_user_folder = os.path.join(
                app.config['UPLOAD_FOLDER'],
                "Teams",
                user.username,
                file_name
            )

            file_path_cs_java = os.path.join(
                UPLOAD_FOLDER,
                "cs_java_files_to_grade"
            )

            # if file exists, report it's still waiting to be graded
            if not os.path.isfile(file_path_user_folder):
                # saves file to folder, will delete if test failed
                file_data.save(file_path_user_folder)

                # changes file status
                user.files[int(problem_num)-1].status = "Submitted"
                db.session.commit()

                """
                file_ext = file_name.split('.')[1]
                # if file is cpp or python, auto grade
                if file_ext == 'py':
                    if grade_submission(user, file_path_user_folder, file_name, problem_num):
                        update_file_status(user, problem_num, "Solved")
                        update_score(user, int(problem_num))
                    else:
                        update_file_status(user, problem_num, "Failed")
                        os.remove(file_path_user_folder)
                # if java or cs file or cpp, save to cs_java folder to await manual grading
                else:
<<<<<<< HEAD
                """
                copyanything(file_path_user_folder, file_path_cs_java)
=======
                    copyanything(file_path_user_folder, file_path_cs_java)
>>>>>>> 9773e425d9837869abf027c63a6c5b29182d8141

                flash("File " + file_name + " uploaded successfully!")
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

    if file_ext == 'py':
        p = subprocess.Popen(
            ['python', file_path],
            stdin=test_input,
            stdout=user_file_output
        )

    t = threading.Timer(60.0, timeout, [p])
    t.start()
    p.wait()
    t.cancel()
    user_file_output.flush()
    user_file_output.seek(0,0)

    return checkAns(user_file_output.readlines(), test_output.readlines())



@app.route('/admin_update_score', methods = ['GET', 'POST'])
@login_required
def admin_update_score():
    user = g.user
    allowed_statuses = ["Solved", "Failed"]
    allowed_problem_nums = range(1,31)
    form = EditUserScoreForm()
    if user.role == 1:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.teamname.data).first()
            prob_num = form.problem_number.data
            new_status = form.status.data

            file_path_user_folder = os.path.join(
                app.config['UPLOAD_FOLDER'],
                "Teams",
                user.username
            )

            if user != None:
                if int(prob_num) in allowed_problem_nums:
                    if new_status in allowed_statuses:

                        #changes problem status to desired value
                        update_file_status(user, prob_num, new_status)

                        if new_status == "Solved":
                            update_score(user, int(prob_num))
                        elif new_status == "Failed":
                            # if failed, removes file from user folder
                            for user_file in os.listdir(file_path_user_folder):
                                file_ext = user_file.split('.')[1]
                                current_file_name = user_file.split('.')[0]
                                wanted_file_name = user.username+'_'+prob_num
                                if current_file_name == wanted_file_name:
                                    os.remove(os.path.join(file_path_user_folder, wanted_file_name+'.'+file_ext))
                                    break

                        flash("Team "+user.username+" problem num "+prob_num+" updated to "+new_status)
                    else:
                        form.status.errors.append("Invalid Status Update!")
                else:
                    form.problem_number.errors.append("Invalid problem number!")
            else:
                form.teamname.errors.append("Invalid team name!")
        return render_template(
            'admin_update_score.html',
            form = form,
            title = "Manual Edit")
    else:
        redirect(url_for('index'))

""" HELPER FUNCTION BLOCK """
# checks if file is of proper type
def allowed_file(file_name):
    return '.' in file_name and file_name.split('.')[-1] in ALLOWED_EXTENSIONS

def update_file_status(user, problem_num, new_status):
    file_to_update = user.files[int(problem_num)-1]
    file_to_update.status = new_status
    db.session.commit()

def update_score(user, problem_num):
    if problem_num in range(1,11):
        user.score += 10
    elif problem_num in range(11,21):
        user.score += 20
    else:
        user.score += 30
    db.session.commit()

def checkAns(user_file_output, test_output):
    for l, line in enumerate(test_output):
        if l < len(user_file_output):
            if user_file_output[l].strip() != line.strip():
                return False
        else:
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

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise