# app.py

from flask import Flask, request, jsonify
from flask import make_response, render_template
from CASClient import CASClient

app = Flask(__name__)

@app.route('/getmsg/', methods=['GET'])
def respond():
	name = request.args.get("name",None)
	print(f"got name {name}")
	response = {}

	if not name:
		response["ERROR"] = "no name found, please send a name."
	elif str(name).isdigit():
		response["ERROR"] = "name can't be numeric."
	else:
		response["MESSAGE"] = f"Welcome {name} to our awesome platform!!!"

	return jsonify(reponse)

@app.route('/post/', methods=['POST'])
def post_something():
	param = request.form.get('name')
	print(param)

	if param:
		return jsonify({
			"Message": f"Welcome {name} to our awesome platform!!!",
			"METHOD": "POST"
			})
	else:
		return jsonify({
			"ERROR": "no name found, please send a name."
			})

@app.route('/')
def index():

	username = CASClient().authenticate()

	html = render_template('index.html', username=username)
	response = make_response(html)
	return response

if __name__ == '__main__':
	app.run(threaded=True, port=5000)