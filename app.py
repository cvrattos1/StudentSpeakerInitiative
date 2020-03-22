# app.py

from flask import Flask, request, jsonify
from flask import make_response, render_template
from CASClient import CASClient
from sys import argv

app = Flask(__name__, template_folder='.')

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
	# username = CASClient().authenticate()
	# html = render_template('index.html', username=username)
	# response = make_response(html)
	# return response

	return render_template('index.html')

@app.route('/logout', methods=['GET'])
def logout():
	casClient = CASClient()
	casClient.authenticate()
	casClient.logout()
	return redirect('/')

@app.route('/student')
def student():
	return render_template('student.html')

@app.route('/admin')
def admin():
	return render_template('admin.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)