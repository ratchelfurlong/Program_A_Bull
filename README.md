Program_A_Bull App
===============

An application written to host our programming competition's submissions and automated graded.
This application uses Miguel Grinberg's microblog tutorial as a reference/baseline, though I've added much functionality that was not included in his tutorial. This app will handle/handles user registration, login, file uploads, latest submission file serving, and automated grading.

TO DO:
====
- Integrate grading script with actual application
- add test cases for EVERY PROBLEM!!
- test test test!

My attempt at explaining how to run this:
=========================================

- Python 3
- I would recommend you use a virtual env (I use Anaconda-python "conda" virtual envs)

1) Clone this repository

2) Download python packages:

	> pip install flask
	
	> pip install flask-login
	
	> pip install flask-wtf
	
	> pip install sqlalchemy
	 
	> pip install sqlalchemy-migrate

3) Navigate via command-line to <your-file-path>/file_upload_app 

	> python db_create.py
	
	> python run.py

4) go to localhost:5000 to test it
