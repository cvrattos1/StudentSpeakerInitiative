# app.py

from flask import Flask, request, jsonify
from flask import make_response, render_template
from CASClient import CASClient
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
	return redirect('/index')

@app.route('/student', methods=['GET'])
def student():
	username = CASClient().authenticate()
	html = render_template('student.html', username=username)
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