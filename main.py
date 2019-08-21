# Imports
import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

# Vars
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

# Begin Serving
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'many random bytes'

## ROUTES ##

# Index
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

# What is AIM
@app.route('/aim_info')
def aim_info():
	return render_template('aim_info.html', title='AIM Info')

# Fill incidence form
@app.route('/fill_incidence')
def fill_incidence():
	return render_template('fill_incidence.html', title='Web Form')

# Credentials
@app.route('/sign_in')
def sign_in():
	return render_template('sign_in.html', title='Log In')

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