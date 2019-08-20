
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def hello():
	return render_template('index.html', title='AIM')

@app.route('/index2')
def index2():
	return render_template('index2.html', title='AIM Info')