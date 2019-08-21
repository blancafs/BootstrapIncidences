
from flask import Flask
from flask import render_template
from lib.forms import WebForm
import os

#lib.incident, lib.engine

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/aim_info')
def aim_info():
	return render_template('aim_info.html', title='AIM Info')

@app.route('/fill_incidence')
def fill_incidence():
	form = WebForm()
	if form.validate_on_submit():
		engine.dealWithWebForm(form)
	return render_template('fill_incidence.html', title='Web Form', form=form)

@app.route('/sign_in')
def sign_in():
	return render_template('sign_in.html', title='Log In')



