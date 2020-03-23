# app.py

from flask import Flask, request, jsonify
from flask import make_response, render_template
from CASClient import CASClient
from database import *
from sys import argv


app = Flask(__name__, template_folder='.')

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

# @app.route('/', methods=['GET'])
# @app.route('/index', methods=['GET'])
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/logout', methods=['GET'])
def logout():
	casClient = CASClient()
	casClient.authenticate()
	casClient.logout()
	return redirect('/')

@app.route('/student', methods=['GET'])
def student():
	username = CASClient().authenticate()

	database = Database()

	speakers = database.getSpeakers()

	html = render_template('student.html',
						   username=username,
						   speakers=speakers,
						   remaining=database.remainingEndorsements(username),
						   database=database)
	response = make_response(html)

	return response

@app.route('/nominate_flask')
def nominate_flask():
	username = CASClient().authenticate()
	database = Database()

	lname=request.args.get('lname')
	fname=request.args.get('fname')
	descrip=request.args.get('descrip')

	database.nominate(username, fname, lname, descrip)

	speakers = database.getSpeakers()

	html = render_template('student.html',
						   username=username,
						   speakers=speakers,
						   remaining=database.remainingEndorsements(username),
						   database=database)
	response = make_response(html)
	return response
# Should add another layer of authentication
@app.route('/admin', methods=['GET'])
def admin():
	username = CASClient().authenticate()
	html = render_template('admin.html', username=username)
	response = make_response(html)
	return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)