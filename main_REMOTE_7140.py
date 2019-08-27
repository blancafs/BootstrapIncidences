# IMPORTS FOR TESTING
from lib.incidentBase import IncidentBase
from lib.configurator import TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH
from lib.forms import FormBuilder

# Imports
import os

import pandas as pd
from flask import Flask, render_template, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from lib.forms import WebForm
from lib.configurator import USER_DATABASE_PATH

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get information on incident from the database
@app.route('/get_info', methods =['GET', 'POST'])
def get_info():
    id = request.args.get('id')

    #form = engine.retrieveFormFromId(id)
    # Testing code, otherwise done by engine
    ###################
    if id == None:
        print('[main]: get_info(): id is None')
        return render_template('get_info.html', form=FormBuilder.buildEmptyForm())
    else:
        id = int(id)
        incidentBase = IncidentBase(None, TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH)
        entry_df = incidentBase.getEntry(id)
        print(entry_df)
        form = FormBuilder.buildFromEntry(entry_df)
        form.id = id
    ####################
    return render_template('get_info.html', form=form)


## TESTING ##
@app.route('/success', methods=['GET', 'POST'])
def success():
    ret_string = '''
                <!doctype html>
                <title>Success</title>
                <h1>Success</h1>
                '''
    if request.method == 'POST':
        return ret_string + '<h1>POST + ' + str(request.form.keys())
    elif request.method == 'GET':
        return ret_string + '<h1>GET + ' + str(request.args.get('title'))
    else:
        return ret_string