# Imports
import os

# Custom imports
from lib.engine import Engine
from lib.forms import WebForm
from lib.configurator import UPLOADS_PATH, PORT

# Web imports
from flask import Flask, render_template, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename

# Vars
UPLOAD_FOLDER = UPLOADS_PATH[:-1]
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
SECRET_KEY = os.urandom(32)

# Begin Serving
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize engine
engine = Engine()

## ROUTES ##


# Index
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    Renders the initial page with the options for actions on the website.
    :return: initial html page
    """
    return render_template('index.html')

# What is AIM
@app.route('/aim_info', methods=['GET', 'POST'])
def aim_info():
    """
    This method returns the page that describes the website's purpose.
    :return: information html page
    """
    return render_template('aim_info.html', title='AIM Info')

# Fill incidence form
@app.route('/fill_incidence', methods=['GET', 'POST'])
def fill_incidence():
    """
    This method creates a web form for the user to fill in an incidence, once the information is submitted
    the engine will handle the information, add it to the database and so on.
    :return: html page for filling in web form
    """
    form = WebForm()
    # If form filled correctly then save, and redirect to the information page
    if (request.values.get("submit_incidence")=="Submit") and (request.values.get('aviso_calidad') is not None):
        id = engine.dealWithWebForm(form)
        return redirect(url_for('get_info', id=id))
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

        # File is correct, attempt to save it, process it and delete it
        if file and allowed_file(file.filename):
            # Retrieve and save file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Deal with file
            id = engine.dealWithFile(file_path)
            return redirect(url_for('get_info', id=id))

    flash('Method was not post')
    return redirect(url_for('upload_form'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get information on incident from the database
@app.route('/get_info', methods=['GET', 'POST'])
def get_info():
    # If no category or sub category, then just display the requested id
        id = request.args.get('id')
        form = engine.retrieveFormFromId(id)
        return render_template('get_info.html', form=form)

@app.route('/get_info/configure', methods=['GET',"POST"])
def configure():
    id = request.args.get('id')
    category = request.args.get('category')
    sub_category = request.args.get('sub-category')
    engine.configureIncident(id,category,sub_category)
    return redirect(url_for('get_info', id=id))

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

### MAIN ###
if __name__=='__main__':
    app.run(host='0.0.0.0', port=PORT)
    print('[main]: main(): Server is listening on port:', PORT)
