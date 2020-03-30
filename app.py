# app.py

from flask import Flask, request, jsonify
from flask import make_response, redirect, render_template, url_for
from CASClient import CASClient
from database import *
from sys import argv


app = Flask(__name__)

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

class canidateprofile:
  def __init__(self, speakerid, name, description, endorsement, totalcount):
    self.speakerid = speakerid  
    self.name = name
    self.description = description
    self.endorsement = endorsement
    self.totalcount = totalcount

def filllist(username, database, request):
    
    finallist = []
    
    if request is "endorsement":
        speakers = database.getSpeakers() 
        for speaker in speakers:
            speakerid = speaker
            name = database.getSpeakerFirstName(speaker) + " " + database.getSpeakerLastName(speaker)
            description = database.getSpeakerDescription(speaker)
            endorsement = database.hasEndorsed(username,speaker)
            totalcount = database.getSpeakerEndorsements(speaker)
            tempcanidate = canidateprofile(speakerid, name, description, endorsement, totalcount)
            finallist.append(tempcanidate)   
    
    else:
        speakers = database.getEndorsed(2)
        print(speakers)
        for speaker in speakers:
            speakerid = speaker
            name = database.getSpeakerFirstName(speaker) + " " + database.getSpeakerLastName(speaker)
            description = database.getSpeakerDescription(speaker)
            totalcount = database.getSpeakerVotes(speaker)
            tempcanidate = canidateprofile(speakerid, name, description, None, totalcount)
            finallist.append(tempcanidate)  
    
    return finallist
    

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

    html = render_template('sHome.html',
    					   username=username)
    response = make_response(html)
    return response

@app.route('/sNom')
def sNom():
    username = CASClient().authenticate()
    database = Database()
    nomname = database.hasNominated(username)
    if nomname == 1:
        html = render_template('sNoNom.html',
                               username=username)
    else:
        errorMsg = request.args.get('errorMsg')
        if errorMsg is None:
            errorMsg = ''
        html = render_template('sNom.html',
                               username=username,
                               errorMsg=errorMsg)
    
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
        return redirect(url_for('sNom',
						   errorMsg=errorMsg))
    
    if not database.hasNominated(username):
        database.nominate(username, fname, lname, descrip)
    
    endorsementlist = filllist(username, database, "endorsement")
    remaining=database.remainingEndorsements(username)  
    html = render_template('sEndorse.html',
						   username=username,
                           endorsementlist = endorsementlist,
						   remaining = remaining)
    response = make_response(html)
    return response

@app.route('/endorse_flask')
def endorse_flask():
    username = CASClient().authenticate()
    database = Database()
    speakerid =request.args.get('speakerid')
    status = request.args.get('status')
    
    if status == "Endorse":
        if (database.remainingEndorsements(username)) > 0 :
            database.endorse(username, speakerid, 1)
    elif status == "Unendorse":
        database.unendorse(username, speakerid, 1)
    
    endorsementlist = filllist(username, database, "endorsement")
    remaining = database.remainingEndorsements(username) 

    html = render_template('sEndorse.html',
						   username=username,
                           endorsementlist = endorsementlist,
						   remaining = remaining)
    response = make_response(html)
    return response


@app.route('/sEndorse', methods=['GET'])
def sEndorse():
    username = CASClient().authenticate()
    database = Database()
    endorsementlist = filllist(username, database, "endorsement")
    remaining = database.remainingEndorsements(username) 
    html = render_template('sEndorse.html',
                               username = username,
                               endorsementlist = endorsementlist,
                               remaining = remaining)
    response = make_response(html)

    return response


@app.route('/sVote', methods=['GET'])
def sVote():
    username = CASClient().authenticate()
    database = Database()
    votingperiod = "True"
    if votingperiod:
        if database.hasVoted(username):
            html = render_template('salreadyVote.html',
                                username=username)
            response = make_response(html)
        else:
            votinglist = filllist(username,database, "voting")
            html = render_template('sVote.html',
                                   username=username,
                                   votinglist = votinglist)
            response = make_response(html)
    else:
        html = render_template('snoVote.html',
                                username=username)
        response = make_response(html)
    
    return response


# Should add another layer of authentication
@app.route('/aHome', methods=['GET'])
def admin():
	username = CASClient().authenticate()
	database = Database()
	html = render_template('aHome.html',
							username=username)
	response = make_response(html)
	return response

@app.route('/aNoms', methods=['GET'])
def aNoms():
    username = CASClient().authenticate()
    database = Database()
    speakers = database.getSpeakers()
    html = render_template('aNoms.html',
                            username=username,
                            speakers=speakers,
                            database=database)
    response = make_response(html)
    return response

@app.route('/aVotes', methods=['GET'])
def aVotes():
    username = CASClient().authenticate()
    database = Database()

    html = render_template('aVotes.html',
                            username=username)
    response = make_response(html)
    return response

@app.route('/aReports', methods=['GET'])
def aReports():
    username = CASClient().authenticate()
    database = Database()

    html = render_template('aReports.html',
                            username=username)
    response = make_response(html)
    return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)