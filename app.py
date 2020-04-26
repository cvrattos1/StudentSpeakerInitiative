# app.py
from random import shuffle
from flask import Flask, request, jsonify
from flask import make_response, redirect, render_template, url_for
from CASClient import CASClient
from databasev2 import Database
from sys import argv, stderr
import cloudinary as Cloud
import cloudinary.uploader
import datetime
import json
from flask_mail import Mail, Message
import os

from student import Student
from faculty import Faculty
from speaker import Speaker
from cycle import Cycle
from report import Report
from conversation import Conversation
from datetime import date
import pustatus

from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from userAccount import userAccount

UNLIMITED_VALUE = 2147483647

login_manager = LoginManager()

app = Flask(__name__)

login_manager.init_app(app)

login_manager.login_view = "/sHome"

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

cloudinary.config(cloud_name=os.environ['CLOUD_NAME'],
				  api_key=os.environ['API_KEY'],
				  api_secret=os.environ['API_SECRET'])

app.config.update(
	DEBUG=True,
	MAIL_USE_TLS=True,
	MAIL_SERVER=os.environ['MAIL_SERVER'],
	MAIL_PORT=587,
	MAIL_USERNAME=os.environ['MAIL_USERNAME'],
	MAIL_PASSWORD=os.environ['MAIL_PASSWORD']
	)
mail = Mail(app)

ldapserver = pustatus.ServerConnection(os.environ['LDAP_USERNAME'], os.environ['MAIL_PASSWORD'])


def filllist(username, database, request):
	finallist = []
	
	if request == "endorsement":
		finallist = database.getSpeakers()

	elif request == "voting":
		finallist = database.getEndorsed(1)
	
	return finallist

def cyclevalidation(cycle):
	if cycle.getName():
		nominating = cycle.getDateNom() > datetime.date.today()
		if nominating:
			voting = False
			endorsing = False
			end = False
		else:
			endorsing = cycle.getDateEndorse() > datetime.date.today()
			if endorsing:
				voting = False
				end = False
			else:
				voting = cycle.getDateVoting() > datetime.date.today()
				if voting:
					end = False
				else:
					end = cycle.getDateEnd() > datetime.date.today()

		# if cycle.getDateEnd() <= datetime.date.today():
		# 	voting = None
		# 	endorsing = None
		# 	nominating = None
		# 	end = True

		# elif cycle.getDateVoting() <= datetime.date.today():
		# 	voting = True
		# 	endorsing = False
		# 	nominating = False

		# else:
		# 	endorsing = cycle.getDateEndorse() <= datetime.date.today()
		# 	if endorsing:
		# 		nominating = False
		# 		voting = False

		# 	else:
		# 		nominating = cycle.getDateNom() <= datetime.date.today()
		# 		if nominating:
		# 			voting = False
		# 			endorsing = False
	else:
		nominating = None
		endorsing = None
		voting = None
		end = None
	
	validation = {"nominating":nominating,"endorsing":endorsing, "voting": voting, "end": end }

	return validation

def uservalidation(username, database):
    student = database.getStudent(username)
    if student:
        return "undergraduates"
    faculty = database.getFaculty(username)
    if faculty:
        return "faculty"
    undergrad = pustatus.isUndergraduate(ldapserver, username)
    if undergrad:
        database.makeStudent(username)
        return "undergraduates"
    fac = pustatus.isFaculty(ldapserver, username)
    if fac:
        database.makeFaculty(username)
        return "faculty"
    return "other"


def checkuser(role, pageType):
    
    if role != pageType:
        return False
    else:
        return True
        

@login_manager.user_loader
def load_user(user_id):
	database = Database()
	role = uservalidation(user_id, database)
	return userAccount(user_id, role)
		
# @app.route('/', methods=['GET'])
# @app.route('/index', methods=['GET'])

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')


@app.route('/aboutus')
def aboutus():
	return render_template('aboutus.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
   logout_user()
   casClient = CASClient()
   casClient.authenticate()
   casClient.logout()
   return redirect('/')

	

@app.route('/sHome', methods=['GET', 'POST'])
def student():
    username = CASClient().authenticate()
    undergrad = pustatus.isUndergraduate(ldapserver, username)
    if not undergrad:
        database = Database()
        if (database.adminAuthenticate(username) == 0):
			
            html = render_template('loginfail.html',
								   username=username,
                                   pageType= "undergraduates")
            response = make_response(html)
			   
            return response
        else:
            uservalidation(username, database)
			
            useraccount = userAccount(username,"undergraduates")
            login_user(useraccount)
		
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            if cycle.getName() is None:
                exists = 0
            else:
                exists = 1
            html = render_template('sHome.html',
								   username=username,
								   exists=exists,
								   cycle=cycle,
								   validation=validation
								   )
            response = make_response(html)
			   
            return response    
	   
    else:
        database = Database()
        uservalidation(username, database)
        useraccount = userAccount(username, "undergraduates")
        login_user(useraccount)
        cycle = database.getCycle()
        validation = cyclevalidation(cycle)
        if cycle.getName() is None:
            exists = 0 
        else:
            exists = 1
        html = render_template('sHome.html',
							   username=username,
							   exists=exists,
							   cycle=cycle,
							   validation=validation
							   )
        response = make_response(html)
		   
        return response
    
@app.route('/fHome', methods=['GET', 'POST'])
def faculty():
	 
    username = CASClient().authenticate()
    faculty = pustatus.isFaculty(ldapserver, username)
    if not faculty:
        database = Database()
        if (database.adminAuthenticate(username) == 0):
			
            html = render_template('loginfail.html',
								   username=username,
                                   pageType= "faculty")
            response = make_response(html)
			   
            return response
        else:
            uservalidation(username, database)
			
            useraccount = userAccount(username,"faculty")
            login_user(useraccount)
		
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            if cycle.getName() is None:
                exists = 0
            else:
                exists = 1
            html = render_template('fHome.html',
								   username=username,
								   exists=exists,
								   cycle=cycle,
								   validation=validation
								   )
            response = make_response(html)
			   
            return response    
	   
    else:
        database = Database()
        uservalidation(username, database)
        useraccount = userAccount(username, "faculty")
        login_user(useraccount)
        cycle = database.getCycle()
        validation = cyclevalidation(cycle)
        if cycle.getName() is None:
            exists = 0 
        else:
            exists = 1
        html = render_template('fHome.html',
							   username=username,
							   exists=exists,
							   cycle=cycle,
							   validation=validation
							   )
        response = make_response(html)
		   
        return response


@app.route('/sNom')
@login_required
def sNom():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	
	cycle = database.getCycle()
	if cycle.getName():
		remaining = database.remainingNominations(username)
	else:
		remaining=None;
	validation = cyclevalidation(cycle)
	errorMsg = request.args.get('errorMsg')
	if errorMsg is None:
		errorMsg = ''
	html = render_template('sNom.html',
						   username=username,
						   errorMsg=errorMsg,
						   cycle=cycle,
						   remaining=remaining,
						   validation=validation)

	print("validation: " + str(validation['voting']) + str(validation['endorsing']) + str(validation['nominating']))

	response = make_response(html)
	return response

@app.route('/nominate_flask', methods=['POST'])
@login_required
def nominate_flask():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	
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
		
	result = Cloud.uploader.upload(argdict['Image'], use_filename='true', filename=(argdict['Image'].filename), folder='SSI', width=400, height=500, crop="limit")
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
@login_required
def new_cycle():
	username = current_user.id
	database = Database()
	
	
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

	elif (argdict["Nomination Date Begins"] >= argdict["Enosorsement Date Begins"]
			or argdict["Enosorsement Date Begins"] >= argdict["Voting Date Begins"]
			or argdict["Voting Date Begins"] >= enddate):
		errorMsg = "The Nomination, Endorsement and Voting period must be chronological and cannot have the " \
				   "same starting date. Please check your dates and resubmit."

				
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
	
	rolloverThresh = request.args.get('rolloverthresh')
	rolloverNom = request.args.get('rollovernom')
	rolloverEnd = request.args.get('rolloverend')
	rolloverVot = request.args.get('rollovervot')
	
	database.adjustDatabase(rolloverNom, rolloverEnd, rolloverVot, rolloverThresh)
	today = date.today()
	database.addLog(today, username, 2, str(enddate))
	
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
	
	
	
	return redirect('aHome')


@app.route('/endorse_flask', methods=['POST'])
@login_required
def endorse_flask():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	
	cycle = database.getCycle()
	endorsed = request.form.get('list')
	endorsed = endorsed.split(',')

	student = database.getStudent(username)
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
@login_required
def vote_flask():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	cycle = database.getCycle()
	voted = request.form.getlist('check')
	speakids = request.form.getlist('speakid')

	student = database.getStudent(username)
	if student.getVotes():
		return redirect('sHome')

	error = False
	if cycle.getVoteNum() != 'unlimited':
		count = 0
		for vote in voted:
			if vote != '':
				if int(vote) >= 0:
					count += int(vote)
				else:
					error = True
		print(count)

		if count > int(cycle.getVoteNum()) or error == True:
			return redirect('sVote')

	for i in range(len(voted)):
		if voted[i] != '':
			database.vote(username, speakids[i], voted[i])
	return redirect('sVote')


@app.route('/flag_flask')
@login_required
def flag_flask():
	username = current_user.id
	database = Database()
	
	cycle = database.getCycle()
	reason = request.args.get('reason')
	speakerid = request.args.get('speakerid')

	database.flag(username, speakerid, reason)
	try:
		recipient = username[:-1] + "@princeton.edu"
		msg = Message("Hello",sender="ssidev@princeton.edu",recipients=[recipient])
		msg.body = "Dear Student,\n\nYour flag request has been submitted to the Students' Speakers Initiative comittee for review. Thank you for your feedback.\n\nSincerely,\nThe Students' Speakers Initiative"
		msg.subject = "Students' Speakers Initiative Flag"
		mail.send(msg)
		print('Mail sent to ' + recipient)
	except Exception as e:
		print(str(e))
		print("NOOOOOO")
		print(username[:-1] + "@princeton.edu")

	return redirect('sEndorse')


@app.route('/remove_nomination')
@login_required
def remove_nomination():
	username = current_user.id
	database = Database()

	speakerid = request.args.get('speakerid')
	today = date.today()
	speakerinfo = database.getSpeaker(speakerid)    # returns Speaker object
	database.addLog(today, username, 4, speakerinfo.getName())
	
	database.removeNomination(speakerid)

	return redirect('aReports')


@app.route('/dismiss_flag')
@login_required
def dismiss_flag():
	username = current_user.id
	database = Database()

	speakerid = request.args.get('speakerid')
	database.dismissFlag(speakerid)

	today = date.today()
	speakerinfo = database.getSpeaker(speakerid)
	database.addLog(today, username, 3, speakerinfo.getName())

	return redirect('aReports')

@app.route('/ssearch', methods=['GET'])
def ssearch():
	try:
		# Name is the name that the user types in the search bar
		name = request.args.get('name')
		if name is None:
			name = ''

		database = Database()
		speakers = database.searchEndorsements(name)

		html = render_template('sresults.html', speakers=speakers)
		response = make_response(html)
	except Exception as e:
		print(e, file=stderr)
		html = "A search related error occurred"
		response = make_response(html)
	return response

@app.route('/adminsearch', methods=['GET'])
def adminsearch():
	try:
		name = request.args.get('name')
		if name is None:
			name = ''

		database = Database()
		info = database.searchAdminLogs(name)
		admins = database.returnAdmins()
		html = render_template('adminresults.html',
								info=info)
		response = make_response(html)
	except Exception as e:
		print(e, file=stderr)
		html= "A search related error occurred"
		response = make_response(html)
	return response

@app.route('/sEndorse', methods=['GET'])
@login_required
def sEndorse():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	
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
@login_required
def sVote():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()

	cycle = database.getCycle()
	user = database.getStudent(username)
	validation = cyclevalidation(cycle)
	
	if cycle.getName():
		speakers = database.getEndorsed(cycle.getThreshold())
		if user:
			hasvoted = user.getVotes()
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
@login_required
def scNom():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	cycle = database.getCycle()
	if cycle.getName():
		remaining = database.remainingccNominations(username)
	else:
		remaining=None;
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
@login_required
def ccnominate_flask():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	
	cycle = database.getCycle()
	validation = cyclevalidation(cycle)
	remaining = database.remainingccNominations(username)

	names = request.form.getlist('name')
	descrips = request.form.getlist('descrip')
	links = request.form.getlist('links')
	files = request.files.getlist("file")


	spkrCount = len(names)
	argerror = False
	# Checks that there is an equal number of inputs for each of the fields
	if spkrCount != len(descrips) or spkrCount != len(links) or spkrCount != len(files):
		print("Failed ccnomination: inconsistent number of fields filled out")
		return redirect('scNom')
	# Checks that the number of inputs is not less than two or more than four.
	if not argerror:
		if spkrCount < 2 or spkrCount > 4:
			print("Failed ccnomination: unacceptable number of speakers")
			return redirect('scNom')

	# Checks that none of the files are empty; if not empty, uploads the image to cloudinary and appends it to images.
	images = []
	for file in files:
		if file.filename == '':
			print("Failed ccnomination: empty file")
			return redirect('scNom')

		result = Cloud.uploader.upload(file, use_filename='true', filename=(file.filename), folder='SSI')
		images.append(result['secure_url'])

	conversation = {}
	for i in range(spkrCount):
		if names[i] == '' or descrips[i] == '' or links[i] == '':
			print("Failed ccnomination: empty field")
			return redirect('scNom')
		spkr = [ names[i], descrips[i], links[i], images[i] ]
		conversation.update({str(i):spkr})


	conzip = json.dumps(conversation)
	
	if remaining:
		database.ccnominate(username,
						cycle.getName(),
						conzip)
	
	return redirect('scEndorse')
	#-------------------------------------------------------------------------
	# CODE BELOW IS OLD; DO NOT USE PLEASE
	# argdict = {"Name of First Speaker":request.form['name1'],
			 #   "Description of First Speaker":request.form['descrip1'],
			 #   "Link to works of First Speaker":request.form['links1'],
			 #   "Image of First Speaker":request.files['file1'],
			 #   "Name of Second Speaker":request.form['name2'],
			 #   "Description of Second Speaker":request.form['descrip2'],
			 #   "Link to works of Second Speaker":request.form['links2'],
			 #   "Image of Second Speaker":request.files['file2']
			 #   }
	# argerror = False
	# wrongarg = []
	# for key, value in argdict.items():
	#     if not value :
	#         wrongarg.append(key)
	#         argerror = True
	# if (argerror):
	#     errorMsg = None
	#     for error in wrongarg:
	#         error = error + " can't be empty.\n"
	#         if not errorMsg:
	#             errorMsg = error
	#         else:
	#             errorMsg = errorMsg + error
	#     html = render_template('scNom.html',
				#               username=username,
				#               errorMsg=errorMsg,
				#               cycle=cycle,
				#               remaining = remaining,
				#               validation = validation,
				#               name1 = argdict['Name of First Speaker'], 
				#               descrip1 = argdict['Description of First Speaker'], 
				#               links1 = argdict['Link to works of First Speaker'],
				#               name2 = argdict['Name of Second Speaker'], 
				#               descrip2 = argdict['Description of Second Speaker'], 
				#               links2 = argdict['Link to works of Second Speaker'])
	#     response = make_response(html)
	#     return response
	# result = Cloud.uploader.upload(argdict['Image of First Speaker'], use_filename='true', filename=(argdict['Image of First Speaker'].filename), folder='SSI')
	# result2 = Cloud.uploader.upload(argdict['Image of Second Speaker'], use_filename='true', filename=(argdict['Image of Second Speaker'].filename), folder='SSI')
	# imglink1 = result['secure_url']
	# imglink2 = result2['secure_url']

	# conversation = {"1":[argdict['Name of First Speaker'], argdict['Description of First Speaker'], argdict['Link to works of First Speaker'],imglink1],
	#                 "2":[argdict['Name of Second Speaker'], argdict['Description of Second Speaker'], argdict['Link to works of Second Speaker'],imglink2]}
	


@app.route('/ccendorse_flask', methods=['POST'])
@login_required
def ccendorse_flask():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	cycle = database.getCycle()
	cyclevalidation(cycle)
	endorsed = request.form.getlist('check')
	student = database.getStudent(username)
	print(student)
	print(student.getccEndorsements())
	if student.getccEndorsements():
		return redirect('sHome')
	if cycle.getEndorseNum() != 'unlimited':
		if len(endorsed) > int(cycle.getEndorseNum()):
			#some error
			return redirect('scEndorse')

	for converseid in endorsed:
		database.ccendorse(username,converseid, 1)

	return redirect('scEndorse')

@app.route('/fpromote_flask', methods=['POST'])
@login_required
def fpromote_flask():
	checkuser(current_user.getRole(), "faculty")
	username = current_user.id
	database = Database()
	cycle = database.getCycle()
	cyclevalidation(cycle)
	endorsed = request.form.getlist('check')
	student = database.getStudent(username)
	print(student)
	print(student.getccEndorsements())
	if student.getccEndorsements():
		return redirect('fHome')
	
	for converseid in endorsed:
		database.ccendorse(username,converseid, 1)

	return redirect('scEndorse')



@app.route('/ccvote_flask' , methods=['POST'])
@login_required
def ccvote_flask():
    checkuser(current_user.getRole(), "undergraduates")
    username = current_user.id
    database = Database()
    cycle = database.getCycle()
    cyclevalidation(cycle)
    voted = request.form.getlist('check')
    converseid = request.form.getlist('converseid')
    student = database.getStudent(username)
	
    if student.getccVotes():
        return redirect('sHome')

    error = False
    if cycle.getVoteNum() != 'unlimited':
        count = 0
        for vote in voted:
            if vote != '':
                if int(vote) >= 0:
                    count += int(vote)
                else:
                    error = True

        if count > int(cycle.getVoteNum()) or error == True:
            return redirect('scVote')

    for i in range(len(voted)):
        if voted[i] != '':
            database.ccvote(username, converseid[i], voted[i])
    return redirect('scVote')


@app.route('/scEndorse', methods=['GET'])
@login_required
def scEndorse():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	cycle = database.getCycle()
	validation = cyclevalidation(cycle)
	student = database.getStudent(username)
	if student:
		hasendorsed = student.getccEndorsements()
	else:
		hasendorsed = 0
	conversations = database.getConversations(1)
	html = render_template('scEndorse.html',
						   username= username,
						   cycle= cycle,
						   conversations = conversations,
						   validation = validation,
						   hasendorsed = hasendorsed
						   )
	response = make_response(html)
	   
	return response

@app.route('/fPromote', methods=['GET'])
@login_required
def fPromote():
    pageType = "faculty"
    username = current_user.id
    # check = checkuser(current_user.getRole(), pageType)
    check = True
    if not check:
        html = render_template('loginfail.html',
								   username=username,
                                   pageType = pageType)
        response = make_response(html)
			   
        return response
    else:
    	database = Database()
    	cycle = database.getCycle()
    	validation = cyclevalidation(cycle)
    	faculty = database.getFaculty(username)
    	if faculty:
    		haspromoted = faculty.getEndorsements()
    	else:
    		haspromoted = 0
    	conversations = database.getConversations(0)
    	html = render_template('fPromote.html',
    						   username= username,
    						   cycle= cycle,
    						   conversations = conversations,
    						   validation = validation,
    						   haspromoted = haspromoted
    						   )
    	response = make_response(html)
    	   
    	return response


@app.route('/scVote', methods=['GET'])
@login_required
def scVote():
	checkuser(current_user.getRole(), "undergraduates")
	username = current_user.id
	database = Database()
	
	cycle = database.getCycle()
	student = database.getStudent(username)
	validation = cyclevalidation(cycle)
	
	if cycle.getName():
		conversations = database.getccEndorsed(cycle.getThreshold())
		if student:
			hasvoted = student.getccVotes()
		else:
			hasvoted = 0
	else:
		conversations = None
		hasvoted = None
	
	html = render_template('scVote.html',
						   username=username,
						   cycle=cycle,
						   conversations=conversations,
						   validation = validation,
						   hasvoted = hasvoted
						   )
	response = make_response(html)
	return response


@app.route('/sAdminLogs', methods=['GET'])
@login_required
def sAdminLogs(): 
	username = current_user.id
	database = Database()
	info = database.returnAdminLogs()
	admins = database.returnAdmins()

	html = render_template('sAdminLogs.html',
							admins=admins, 
							info=info)
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
	if cycle.getName() is None:
		exists = 0
	else:
		exists = 1
	admins = database.returnAdmins()
	html = render_template('aHome.html',
						   username=username,
						   admins=admins,
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
	if cycle.getName() is None:
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

@app.route('/acNoms', methods=['GET'])
def acNoms():
	username = CASClient().authenticate()
	database = Database()

	cycle = database.getCycle()
	if cycle.getName() is None:
		exists = 0
	else:
		exists = 1

	conversations = database.getConversations(0)
	promotedconversations = database.getConversations(1)
    
	html = render_template('acNoms.html',
						   username=username,
						   conversations = conversations,
						   promotedconversations = promotedconversations,
                           exists = exists
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
	if cycle.getName() is None:
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

@app.route('/aCreateCycle')
@login_required
def aCreateCycle_flask():
	username = current_user.id
	database = Database()
	
	html = render_template('aCreateCycle.html',
						   username=username,
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
	if cycle.getName() is None:
		exists = 0
	else:
		exists = 1

	reports = database.getReports()
	speakers = []
	for report in reports:
		print(report.getSpeakid())
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
	username = CASClient().authenticate()
	database = Database()
	if database.adminAuthenticate(newAdmin) != 1:  # can't double add
		database.addAdmin(newAdmin)
		today = date.today()					   # add action to DB
		database.addLog(today, username, 0, newAdmin)
	return redirect(url_for('admin'))

@app.route('/removeAdmin', methods=['GET'])
def removeAdmin():
	oldAdmin = request.args.get('oldAdmin')
	username = CASClient().authenticate()
	database = Database()
	if database.returnCount('admin') != 1 and oldAdmin != "":  # can't delete last admin or empty admin
		database.removeAdmin(oldAdmin)
		today = date.today()					   # add action to DB
		database.addLog(today, username, 1, oldAdmin)
	return redirect(url_for('admin'))

@app.route('/aAdminLogs', methods=['GET'])
def aAdminLogs(): 
	username = CASClient().authenticate()
	database = Database()

	if database.adminAuthenticate(username) == 0:
		html = render_template('index.html',
								errorMsg = 'Not authorized')
		response = make_response(html)
		   
		return response

	info = database.returnAdminLogs()
	admins = database.returnAdmins()

	html = render_template('aAdminLogs.html',
							admins=admins, 
							info=info)
	response = make_response(html)
	return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)

