# Imports
import os
import pandas as pd
from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from lib.forms import WebForm, SignInForm
from lib.configurator import USER_DATABASE_PATH
from lib.models import User, UserDB

# Vars
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
SECRET_KEY = os.urandom(32)

#lib.incident, lib.engine
# Begin Serving
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration (database either creates csv file or reads it)
user_db = UserDB(path=USER_DATABASE_PATH)

## ROUTES ##

# Index
@app.route('/index', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

# What is AIM
@app.route('/aim_info', methods=['GET', 'POST'])
def aim_info():
	return render_template('aim_info.html', title='AIM Info')

# Fill incidence form
@app.route('/fill_incidence', methods=['GET', 'POST'])
def fill_incidence():
	if session['current_user']=='logout':
		return render_template('index.html')
	else:
		form = WebForm()
		if form.validate_on_submit():
			engine.dealWithWebForm(form)
		return render_template('fill_incidence.html', title='Web Form', form=form)


# Credentials
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	session['current_user'] = 'logout'
	signin_form = SignInForm()
	if signin_form.submit.data:
		print(signin_form.email.data)
		checked = user_db.checkUser(signin_form.email.data, signin_form.password.data)
		print('checked ', checked)
		if checked>0:
			session['current_user'] = user.getEmail()
			return redirect('index')
	return render_template('login.html', title='Log In', form=signin_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	session['current_user'] = 'logout'
	print(session['current_user'])
	reg_form = SignInForm()
	print(reg_form.submit.data)
	if reg_form.submit.data:
		user = User(reg_form.username.data, reg_form.email.data, reg_form.password.data)
		print(reg_form.username.data, reg_form.email.data)
		successful = user_db.addUser(user)
		print('successful ', successful)
		if successful>0:
			session['current_user'] = user.getEmail()
			print('added user successfully!!!!!!!!! and logged in')
			return redirect('index')
		else:
			return render_template('register.html')
	return render_template('register.html', title='Register', form=reg_form)


# Upload incident pages
@app.route('/upload_form', methods=['GET', 'POST'])
def upload_form():
	if not session['current_user']=='logout':
		return render_template('upload_form.html', title='Upload')
	return render_template('index.html')

@app.route('/uploadFile', methods=['GET', 'POST'])
def uploadFile():
	if request.method == 'POST':
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('File name was empty')
			return redirect(url_for('upload_form'))
		if file and allowed_file(file.filename):
			flash('Success')
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('success'))
	flash('Method was not post')
	return redirect(url_for('upload_form'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


## TESTING ##
@app.route('/success')
def success():
	return '''
	    <!doctype html>
	    <title>Success</title>
	    <h1>Success"</h1>
	    '''