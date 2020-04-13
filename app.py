# app.py
from random import shuffle
from flask import Flask, request, jsonify
from flask import make_response, redirect, render_template, url_for
from CASClient import CASClient
from databasev2 import Database
from sys import argv
import cloudinary as Cloud
import cloudinary.uploader
import datetime

from student import Student
from speaker import Speaker
from cycle import Cycle
from report import Report
from conversation import Conversation

# from flask_login import LoginManager

UNLIMITED_VALUE = 2147483647

app = Flask(__name__)

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

cloudinary.config(cloud_name='dqp1yoed2',
				  api_key='129874246392789',
				  api_secret='wovIZCIrF_S2yEE5mM1b2ha5lao')


def filllist(username, database, request):
	finallist = []
	
	if request == "endorsement":
		finallist = database.getSpeakers()

	elif request == "voting":
		finallist = database.getEndorsed(1)
	
	return finallist

def cyclevalidation(cycle):
	if cycle:
		nominating = cycle.getDateNom() >= datetime.date.today()
		if nominating:
			endorsing = False
			voting = False
		else:
			endorsing = cycle.getDateEndorse() >= datetime.date.today()
			if endorsing:
				voting = False
			else:
				voting = cycle.getDateVoting() >= datetime.date.today()

	else:
		nominating = None
		endorsing = None
		voting = None
	
	
	validation = {"nominating":nominating,"endorsing":endorsing, "voting": voting }

	return validation

def uservalidation(username, database):
	student = database.getStudent(username)
	if not student:
		database.makeStudent(username)

		
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


@app.route('/sHome', methods=['GET'])
def student():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)

	cycle = database.getCycle()
	if cycle is None:
		exists = 0
	else:
		exists = 1
	html = render_template('sHome.html',
						   username=username,
						   exists=exists,
						   cycle=cycle
						   )
	response = make_response(html)
	   
	return response


@app.route('/sNom')
def sNom():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)

	remaining = database.remainingNominations(username)
	cycle = database.getCycle()
	validation = cyclevalidation(cycle)
	errorMsg = request.args.get('errorMsg')
	if errorMsg is None:
		errorMsg = ''
	html = render_template('sNom.html',
						   username=username,
						   errorMsg=errorMsg,
						   cycle=cycle,
						   remaining=remaining,
						   validation = validation)

	response = make_response(html)
	return response


@app.route('/nominate_flask', methods=['POST'])
def nominate_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	remaining = database.remainingNominations(username)
	validation = cyclevalidation(cycle)
	print(remaining)
	argdict = {"Name of Nomination":request.form['name'],
			   "Description":request.form['descrip'],
			   "Link to works":request.form['links'],
			   "Image":request.files['file']
			   }
	argerror = False
	wrongarg = []
	for key, value in argdict.items():
		if not value :
			wrongarg.append(key)
			argerror = True
	
	if (argerror):
		errorMsg = None
		for error in wrongarg:
		   error = error + " can't be empty.\n"
		   if not errorMsg:
			   errorMsg = error
		   else:
			   errorMsg = errorMsg + error
		html = render_template('sNom.html',
								username=username,
								errorMsg=errorMsg,
								cycle=cycle,
								remaining = remaining,
								validation = validation,
								name = argdict['Name of Nomination'], 
								descrip = argdict['Description'], 
								links = argdict['Link to works'])
		response = make_response(html)
		
		return response
		
	result = Cloud.uploader.upload(argdict['Image'], use_filename='true', filename=(argdict['Image'].filename), folder='SSI')
	imglink = result['secure_url']

	if remaining:
		database.nominate(username, 
						  cycle.getName(), 
						  argdict['Name of Nomination'], 
						  argdict['Description'], 
						  argdict['Link to works'], 
						  imglink)
	
	return redirect('sEndorse')

@app.route('/new_cycle')
def new_cycle():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	
	argdict = {"Name of Voting Cycle":request.args.get('cname'),
			   "Number of Nominations":request.args.get('nominatenum'),
			   "Number of Endorsements":request.args.get('endorsenum'),
			   "Number of Votes":request.args.get('votenum'),
			   "Endorsement Threshold":request.args.get('threshold'),
			   "Nomination Date Begins":request.args.get('nomdate'),
			   "Enosorsement Date Begins":request.args.get('endorsedate'),
			   "Voting Date Begins":request.args.get('votingdate')
			   }

	enddate = request.args.get('enddate')
	datecreated = datetime.datetime.now().strftime("%x")
	admin = request.args.get('admin')
	
	argerror = False
	wrongarg = []
	for key, value in argdict.items():
		if not value :
			wrongarg.append(key)
			argerror = True
	

	if (argerror):
		errorMsg = None
		for error in wrongarg:
		   error = error + " can't be empty.\n"
		   if not errorMsg:
			   errorMsg = error
		   else:
			   errorMsg = errorMsg + error
	   
	   
		html = render_template('aCreateCycle.html',
						   username=username,
						   errorMsg = errorMsg,
						   cname = argdict["Name of Voting Cycle"],
						   nominatenum = argdict["Number of Nominations"],
						   endorsenum = argdict["Number of Endorsements"],
						   votenum = argdict["Number of Votes"],
						   threshold = argdict["Endorsement Threshold"],
						   nomdate = argdict["Nomination Date Begins"],
						   endorsedate = argdict["Enosorsement Date Begins"],
						   votingdate = argdict["Voting Date Begins"],
						   enddate = enddate
						   )
		response = make_response(html)
		   
		return response

	admin = request.args.get('admin')

	if (argdict['Number of Nominations'] == "limited"):
		nomination_count = request.args.get('nominatetext')
	else:
		nomination_count = UNLIMITED_VALUE

	if (argdict['Number of Endorsements'] == "limited"):
		endorse_count = request.args.get('endorsetext')
	else:
		endorse_count = UNLIMITED_VALUE

	if (argdict['Number of Votes'] == "limited"):
		vote_count = request.args.get('votetext')
	else:
		vote_count = UNLIMITED_VALUE
		
	database.createCycle(argdict["Name of Voting Cycle"], 
						 datecreated, 
						 admin, 
						 nomination_count, 
						 endorse_count, 
						 vote_count, 
						 argdict["Endorsement Threshold"],
						 argdict["Nomination Date Begins"],
						 argdict["Enosorsement Date Begins"],
						 argdict["Voting Date Begins"],
						 enddate)
	
	rolloverNom = request.args.get('rolloverNom')
	rolloverEnd = request.args.get('rolloverEnd')
	rolloverVot = request.args.get('rolloverVot')

	return redirect('aHome')


@app.route('/endorse_flask', methods=['POST'])
def endorse_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	endorsed = request.form.getlist('check')
	if student.getEndorsements():
		return redirect('sHome')
	if cycle.getEndorseNum() != 'unlimited':
		if len(endorsed) > int(cycle.getEndorseNum()):
			#some error
			return redirect('sEndorse')

	for speakid in endorsed:
		database.endorse(username,speakid, 1)
	return redirect('sEndorse')


@app.route('/vote_flask', methods=['POST'])
def vote_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	voted = request.form.getlist('check')
	if student.getVotes():
		return redirect('sHome')
	print(voted)
	if cycle.getEndorseNum() != 'unlimited':
		if len(voted) > int(cycle.getVoteNum()):
			#some error
			return redirect('sVote')

	for speakid in voted:
		database.vote(username,speakid)
	return redirect('sVote')


@app.route('/reset_flask')
def reset_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
   
	html = render_template('aCreateCycle.html',
						   username=username,
						   )
	response = make_response(html)
	   
	return response


@app.route('/flag_flask')
def flag_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	reason = request.args.get('reason')
	speakerid = request.args.get('speakerid')

	database.flag(username, speakerid, reason)

	return redirect('sEndorse')


@app.route('/remove_nomination')
def remove_nomination():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	speakerid = request.args.get('speakerid')

	database.removeNomination(speakerid)

	return redirect('aReports')


@app.route('/dismiss_flag')
def dismiss_flag():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)

	speakerid = request.args.get('speakerid')
	database.dismissFlag(username, speakerid)

	return redirect('aReports')


@app.route('/sEndorse', methods=['GET'])
def sEndorse():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	validation = cyclevalidation(cycle)
	student = database.getStudent(username)
	if student:
		hasendorsed = student.getEndorsements()
	else:
		hasendorsed = 0
	speakers = database.getSpeakers()
	html = render_template('sEndorse.html',
						   username= username,
						   cycle= cycle,
						   speakers= speakers,
						   validation = validation,
						   hasendorsed = hasendorsed
						   )
	response = make_response(html)
	   
	return response


@app.route('/sVote', methods=['GET'])
def sVote():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	
	cycle = database.getCycle()
	student = database.getStudent(username)
	validation = cyclevalidation(cycle)
	
	if cycle:
		speakers = database.getEndorsed(cycle.getThreshold())
		if student:
			hasvoted = student.getVotes()
		else:
			hasvoted = 0
	else:
		speakers = None
		hasvoted = None
	
	html = render_template('sVote.html',
						   username=username,
						   cycle=cycle,
						   speakers=speakers,
						   validation = validation,
						   hasvoted = hasvoted
						   )
	response = make_response(html)
	   

	return response

@app.route('/scNom')
def scNom():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)

	remaining = database.remainingccNominations(username)
	cycle = database.getCycle()
	validation = cyclevalidation(cycle)
	print(remaining)
	errorMsg = request.args.get('errorMsg')
	if errorMsg is None:
		errorMsg = ''
	html = render_template('scNom.html',
						   username=username,
						   errorMsg=errorMsg,
						   cycle=cycle,
						   remaining=remaining,
						   validation = validation)

	response = make_response(html)
	return response

@app.route('/ccnominate_flask', methods=['POST'])
def ccnominate_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	remaining = database.remainingccNominations(username)
	validation = cyclevalidation(cycle)
	argdict = {"Name of First Speaker":request.form['name1'],
			   "Description of First Speaker":request.form['descrip1'],
			   "Link to works of First Speaker":request.form['links1'],
			   "Image of First Speaker":request.files['file1'],
			   "Name of Second Speaker":request.form['name2'],
			   "Description of Second Speaker":request.form['descrip2'],
			   "Link to works of Second Speaker":request.form['links2'],
			   "Image of Second Speaker":request.files['file2']
			   }
	argerror = False
	wrongarg = []
	for key, value in argdict.items():
		if not value :
			wrongarg.append(key)
			argerror = True
	
	if (argerror):
		errorMsg = None
		for error in wrongarg:
		   error = error + " can't be empty.\n"
		   if not errorMsg:
			   errorMsg = error
		   else:
			   errorMsg = errorMsg + error
		html = render_template('scNom.html',
								username=username,
								errorMsg=errorMsg,
								cycle=cycle,
								remaining = remaining,
								validation = validation,
								name1 = argdict['Name of First Speaker'], 
								descrip1 = argdict['Description of First Speaker'], 
								links1 = argdict['Link to works of First Speaker'],
								name2 = argdict['Name of Second Speaker'], 
								descrip2 = argdict['Description of Second Speaker'], 
								links2 = argdict['Link to works of Second Speaker'])
		response = make_response(html)
		
		return response
		
	result = Cloud.uploader.upload(argdict['Image of First Speaker'], use_filename='true', filename=(argdict['Image of First Speaker'].filename), folder='SSI')
	result2 = Cloud.uploader.upload(argdict['Image of Second Speaker'], use_filename='true', filename=(argdict['Image of Second Speaker'].filename), folder='SSI')
	imglink1 = result['secure_url']
	imglink2 = result2['secure_url']
	
	names = [argdict['Name of First Speaker'],argdict['Name of Second Speaker']]
	descrips = [argdict['Description of First Speaker'], argdict['Description of Second Speaker']]
	links = [argdict['Link to works of First Speaker'], argdict['Link to works of Second Speaker']]
	imglinks = [imglink1,imglink2]
	print("hello")
	if remaining:
		print("hello")
		database.ccnominate(username, 
						  cycle.getName(), 
						  names, 
						  descrips, 
						  links, 
						  imglinks)
	
	return redirect('scEndorse')

@app.route('/ccendorse_flask')
def ccendorse_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	speakerid = request.args.get('speakerid')
	status = request.args.get('status')
	cycle = database.getCycle()
	if status == "Endorse":
		if (database.usedEndorsements(username) < database.getEndAllowance()):
			database.endorse(username, speakerid, 1)
	elif status == "Unendorse":
		database.unendorse(username, speakerid, 1)

	return redirect('sEndorse')


@app.route('/ccvote_flask')
def ccvote_flask():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	speakerid = request.args.get('speakerid')
	if not (database.hasVoted(username)):
		database.vote(username, speakerid)

	cycle = database.getCycle()
	if not cycle:
		exists = 0
	else:
		exists = 1
	html = render_template('sHome.html',
						   username=username,
						   cycle=cycle,
						   exists=exists
						   )
	response = make_response(html)
	   
	return response

@app.route('/scEndorse', methods=['GET'])
def scEndorse():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	cycle = database.getCycle()
	validation = cyclevalidation(cycle)
	student = database.getStudent(username)
	if student:
		hasendorsed = student.getEndorsements()
	else:
		hasendorsed = 0
	speakers = database.getSpeakers()
	html = render_template('scEndorse.html',
						   username= username,
						   cycle= cycle,
						   speakers= speakers,
						   validation = validation,
						   hasendorsed = hasendorsed
						   )
	response = make_response(html)
	   
	return response


@app.route('/scVote', methods=['GET'])
def scVote():
	username = CASClient().authenticate()
	database = Database()
	uservalidation(username, database)
	
	cycle = database.getCycle()
	student = database.getStudent(username)
	validation = cyclevalidation(cycle)
	
	if cycle:
		speakers = database.getEndorsed(cycle.getThreshold())
		if student:
			hasvoted = student.getVotes()
		else:
			hasvoted = 0
	else:
		speakers = None
		hasvoted = None
	
	html = render_template('scVote.html',
						   username=username,
						   cycle=cycle,
						   speakers=speakers,
						   validation = validation,
						   hasvoted = hasvoted
						   )
	response = make_response(html)
	   

	return response

# Should add another layer of authentication
@app.route('/aHome', methods=['GET'])
def admin():
	username = CASClient().authenticate()
	database = Database()

	if database.adminAuthenticate(username) == 0:
		html = render_template('index.html',
								errorMsg = 'Not authorized')
		response = make_response(html)
		   
		return response

	cycle = database.getCycle()
	if cycle is None:
		exists = 0
	else:
		exists = 1

	html = render_template('aHome.html',
						   username=username,
						   cycle=cycle,
						   exists=exists
						   )
	response = make_response(html)
	   
	return response


@app.route('/aNoms', methods=['GET'])
def aNoms():
	username = CASClient().authenticate()
	database = Database()

	cycle = database.getCycle()
	if cycle is None:
		exists = 0
	else:
		exists = 1

	speakers = database.getSpeakers()
	html = render_template('aNoms.html',
						   username=username,
						   speakers=speakers,
						   exists=exists
						   )
	response = make_response(html)
	   
	return response


@app.route('/aVotes', methods=['GET'])
def aVotes():
	username = CASClient().authenticate()
	database = Database()

	if database.adminAuthenticate(username) == 0:
		html = render_template('index.html',
								errorMsg = 'Not authorized')
		response = make_response(html)
		   
		return response

	cycle = database.getCycle()
	if cycle is None:
		exists = 0
		speakers = []
	else:
		exists = 1
		speakers = database.getEndorsed(cycle.getThreshold())

	html = render_template('aVotes.html',
						   username=username,
						   speakers=speakers,
						   exists=exists
						   )
	response = make_response(html)
	   

	return response


@app.route('/aReports', methods=['GET'])
def aReports():
	username = CASClient().authenticate()
	database = Database()

	if database.adminAuthenticate(username) == 0:
		html = render_template('index.html',
							   errorMsg='Not authorized')
		response = make_response(html)
		   
		return response

	cycle = database.getCycle()
	if cycle is None:
		exists = 0
	else:
		exists = 1

	reports = database.getReports()
	speakers = []
	for report in reports:
		speakers.append(database.getSpeaker(report.getSpeakid()))

	html = render_template('aReports.html',
						   username=username,
						   exists=exists,
						   reports=reports,
						   speakers=speakers,
						   length=len(speakers)
						   )
	response = make_response(html)
	   
	return response

@app.route('/addAdmin', methods=['GET'])
def addAdmin():
	newAdmin = request.args.get('newAdmin')
	database = Database()
	if database.adminAuthenticate(newAdmin) != 1:  # can't double add
		database.addAdmin(newAdmin)
	return redirect(url_for('admin'))

@app.route('/removeAdmin', methods=['GET'])
def removeAdmin():
	oldAdmin = request.args.get('oldAdmin')
	database = Database()
	if database.returnCount('admin') != 1:  # can't delete last admin
		database.removeAdmin(oldAdmin)
	return redirect(url_for('admin'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
