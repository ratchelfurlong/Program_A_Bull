file_upload_app
===============

A simple file uploading app written in flask

GOAL (remaining):
====
- upload files to server
- display uploaded files to user
- allow deletion of uploaded files

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

6) go to localhost:5000 to test it
