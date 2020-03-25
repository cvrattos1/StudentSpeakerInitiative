# app.py

from flask import Flask, request, jsonify
from flask import make_response, redirect, render_template, url_for
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
    errorMsg = request.args.get('errorMsg')
    if errorMsg is None:
        errorMsg = ''
    username = CASClient().authenticate()

    database = Database()

    speakers = database.getSpeakers() 
    
    nomname = database.hasNominated(username)
    
    if nomname == 1:
        html = render_template('student1.html',
    						   username=username,
    						   errorMsg=errorMsg,
    						   speakers=speakers,
    						   remaining=database.remainingEndorsements(username),
    						   database=database)
    else: 
        html = render_template('student.html',
    						   username=username,
    						   errorMsg=errorMsg,
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
    if (lname=='' or fname=='' or descrip==''):
        errorMsg = "None of the nomination's fields can be empty."
        return redirect(url_for('student',
						   errorMsg=errorMsg))

    database.nominate(username, fname, lname, descrip)

    speakers = database.getSpeakers()

    html = render_template('student.html',
						   username=username,
						   speakers=speakers,
						   errormsg='',
						   remaining=database.remainingEndorsements(username),
						   database=database)
    response = make_response(html)
    return response
# Should add another layer of authentication
@app.route('/admin', methods=['GET'])
def admin():
	username = CASClient().authenticate()
	database = Database()
	speakers = database.getSpeakers()
	html = render_template('admin.html',
							username=username, 
							speakers=speakers, 
							database=database)
	response = make_response(html)
	return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)