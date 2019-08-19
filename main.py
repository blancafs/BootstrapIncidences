
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def hello():
	return render_template('index.html', title='THIS IS THE TITLE MAN')

@app.route('/index2')
def index2():
	return render_template('index2.html', title='SECOND PAGE MAN')