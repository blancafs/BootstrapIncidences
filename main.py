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

## ROUTES ##

# Index
@app.route('/')
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
	form = WebForm()
	if form.validate_on_submit():
		engine.dealWithWebForm(form)
	return render_template('fill_incidence.html', title='Web Form', form=form)

# Upload incident pages
@app.route('/upload_form', methods=['GET', 'POST'])
def upload_form():
	return render_template('upload_form.html', title='Upload')

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