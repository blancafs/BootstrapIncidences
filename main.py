
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/aim_info')
def aim_info():
	return render_template('aim_info.html', title='AIM Info')

@app.route('/fill_incidence')
def fill_incidence():
	return render_template('fill_incidence.html', title='Web Form')

@app.route('/sign_in')
def sign_in():
	return render_template('sign_in.html', title='Log In')

