import os 

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'msdn_club_usf'

# captcha config
RECAPTCHA_PUBLIC_KEY = '6LcN3_sSAAAAAGzYJz-uftsbD32YYcYdJlAwN7gN'
RECAPTCHA_PRIVATE_KEY = '6LcN3_sSAAAAAK7SUStYesNMiZbtJ1_W9AD6Tmg3'

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = set(['cs', 'py', 'cpp', 'java'])