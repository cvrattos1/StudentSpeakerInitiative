# app.py
from random import shuffle
from flask import Flask, request, jsonify
from flask import make_response, redirect, render_template, url_for
from CASClient import CASClient
from database import *
from sys import argv
import datetime

# from flask_login import LoginManager

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
    
    if request == "endorsement":
        speakers = database.getSpeakers() 
        for speaker in speakers:
            speakerid = speaker
            name = database.getSpeakerFirstName(speaker) + " " + database.getSpeakerLastName(speaker)
            description = database.getSpeakerDescription(speaker)
            endorsement = database.hasEndorsed(username,speaker)
            totalcount = database.getSpeakerEndorsements(speaker)
            tempcanidate = canidateprofile(speakerid, name, description, endorsement, totalcount)
            finallist.append(tempcanidate)   
    
    elif request == "voting":
        speakers = database.getEndorsed(1)
        for speaker in speakers:
            speakerid = speaker
            name = database.getSpeakerFirstName(speaker) + " " + database.getSpeakerLastName(speaker)
            description = database.getSpeakerDescription(speaker)
            totalcount = database.getSpeakerVotes(speaker)
            tempcanidate = canidateprofile(speakerid, name, description, None, totalcount)
            finallist.append(tempcanidate)  
    
    return finallist
    
def renderendorse(username, database):
    templist = filllist(username, database, "endorsement")
    endorselist = []
    for speaker in templist:
        if speaker.endorsement == "Unendorse":
            endorselist.append(speaker)
            templist.remove(speaker)
    # for i in endorselist:
    #     print(i.name)
    # print('')
    # for i in templist:
    #     print(i.name)
    shuffle(templist)
    endorsementlist = endorselist + templist
    # for i in endorsementlist:
    #     print (i.name)
    allowance = database.getEndAllowance()
    remaining=allowance - database.usedEndorsements(username)
    html = render_template('sEndorse.html',
						   username=username,
                           endorsementlist = endorsementlist,
						   remaining = remaining,
                           allowance = allowance)
    response = make_response(html)
    return response
    
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

    cycle = database.getCycleInfo()
    if not cycle:
        exists = 0
    else:
        exists = 1

    html = render_template('sHome.html',
    					   username=username,
                           info = cycle,
                           exists = exists)
    response = make_response(html)
    return response

@app.route('/sNom')
def sNom():
    username = CASClient().authenticate()
    database = Database()
    nomname = database.hasNominated(username)
    votingperiod = database.votePeriod()
    if not votingperiod:
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
    else:
        html = render_template('snotNom.html',
                                username=username)
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
    
    response = renderendorse(username, database)
   
    return response

@app.route('/new_cycle')
def new_cycle():
    username = CASClient().authenticate()
    database = Database()

    if (request.args.get('nominatenum') == '' or request.args.get('endorsenum') == '' or request.args.get('votenum') == '' or request.args.get('votingdate') == '' or request.args.get('threshold') == '' or request.args.get('cname') == ''):
        errorMsg = "None of the nomination's fields can be empty."
        return redirect(url_for('new_cycle',
                                errorMsg=errorMsg,
                                username=username))

    name = request.args.get('cname')
    votingdate = request.args.get('votingdate')
    threshold = request.args.get('threshold')
    datecreated = datetime.datetime.now().strftime("%x")

    if (request.args.get('nominatenum') == "limited"):
        nomination_count = request.args.get('nominatetext')
    else:
        nomination_count = 2147483647

    if (request.args.get('endorsenum') == "limited"):
        endorse_count = request.args.get('endorsetext')
    else:
        endorse_count = 2147483647

    if (request.args.get('votenum') == "limited"):
        vote_count = request.args.get('votetext')
    else:
        vote_count = 2147483647

    database.createCycle(name, datecreated, votingdate, username, endorse_count, vote_count, nomination_count, threshold)

    rolloverNom = request.args.get('rolloverNom')
    rolloverEnd = request.args.get('rolloverEnd')
    rolloverVot = request.args.get('rolloverVot')

    cycle = database.getCycleInfo()
    if not cycle:
        exists = 0
    else:
        exists = 1

    html = render_template('aHome.html',
    					   username=username,
                           info = cycle,
                           exists = exists)
    response = make_response(html)
    return response





@app.route('/endorse_flask')
def endorse_flask():
    username = CASClient().authenticate()
    database = Database()
    speakerid =request.args.get('speakerid')
    status = request.args.get('status')
    
    if status == "Endorse":
        if (database.usedEndorsements(username) < database.getEndAllowance()):
            database.endorse(username, speakerid, 1)
    elif status == "Unendorse":
        database.unendorse(username, speakerid, 1)
    
    response = renderendorse(username, database)
    return response


@app.route('/vote_flask')
def vote_flask():
    username = CASClient().authenticate()
    database = Database()
    speakerid = request.args.get('speakerid')
    if not (database.hasVoted(username)) :
        database.vote(username, speakerid)

    cycle = database.getCycleInfo()
    if not cycle:
        exists = 0
    else:
        exists = 1
    html = render_template('sHome.html',
    					   username=username,
                           info = cycle,
                           exists = exists
                           )
    response = make_response(html)
    return response

@app.route('/reset_flask')
def reset_flask():
    username = CASClient().authenticate()
    database = Database()
    database.adminClearTables()
    if (database.votePeriod()):
        changecycle = "endorsement"
    else:
        changecycle = "voting"
    html = render_template('aCreateCycle.html',
                           username=username,
                           changecycle = changecycle)
    response = make_response(html)
    return response

@app.route('/changeStep_flask')
def changeStep_flask():
    username = CASClient().authenticate()
    database = Database()
    currentPeriod = database.votePeriod()
    if currentPeriod == 1:
        database.changePeriod(0) 
    else:
        database.changePeriod(1) 
    currentPeriod = database.votePeriod()
    if (currentPeriod):
        changecycle = "endorsement"
    else:
        changecycle = "voting"
    html = render_template('aHome.html',
                           username = username,
                           changecycle = changecycle )
    response = make_response(html)
    return response

@app.route('/flag_flask')
def flag_flask():
    username = CASClient().authenticate()
    database = Database()
    reason = request.args.get('reason')
    speakerid = request.args.get('speakerid')

    database.flag(username, speakerid, reason)

    response = renderendorse(username, database)
    return response

@app.route('/remove_nomination')
def remove_nomination():
    username = CASClient().authenticate()
    database = Database()
    speakerid = request.args.get('speakerid')

    database.removeNomination(speakerid)

    return redirect('aReports')

@app.route('/dismiss_flag')
def dismiss_flag():
    username = CASClient().authenticate()
    database = Database()

    speakerid = request.args.get('speakerid')
    database.dismissFlag(username, speakerid)

    return redirect('aReports')

@app.route('/sEndorse', methods=['GET'])
def sEndorse():
    username = CASClient().authenticate()
    database = Database()
    votingperiod = database.votePeriod()
    if not votingperiod:
        response = renderendorse(username, database)
        return response
    else:
        cycle = database.getCycleInfo()
        if not cycle:
            exists = 0
        else:
            exists = 1
        html = render_template('snotEndorse.html',
                                username=username,
                                info=cycle,
                                exists = exists
                               )
        response = make_response(html)
    
        return response


@app.route('/sVote', methods=['GET'])
def sVote():
    username = CASClient().authenticate()
    database = Database()
    votingperiod = database.votePeriod()
    if votingperiod:
        if database.hasVoted(username):
            html = render_template('salreadyVote.html',
                                username=username)
            response = make_response(html)
        else:
            votinglist = filllist(username,database, "voting")
            shuffle(votinglist)
            html = render_template('sVote.html',
                                   username=username,
                                   votinglist = votinglist)
            response = make_response(html)
    else:
        cycle = database.getCycleInfo()
        if not cycle:
            exists = 0
        else:
            exists = 1
        html = render_template('snotVote.html',
                                username=username,
                                info = cycle,
                                exists = exists)
        response = make_response(html)
    
    return response


# Should add another layer of authentication
@app.route('/aHome', methods=['GET'])
def admin():
    username = CASClient().authenticate()
    database = Database()

    if (database.votePeriod()):
        changecycle = "endorsement"
    else:
        changecycle = "voting"

    cycle = database.getCycleInfo()
    if not cycle:
        exists = 0
    else:
        exists = 1

    html = render_template('aHome.html',
                           username=username,
                           changecycle = changecycle,
                           info = cycle,
                           exists = exists
                           )
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
    votinglist = filllist(username,database, "voting")
    html = render_template('aVotes.html',
                           username=username,
                           votinglist = votinglist)
    response = make_response(html)
    
    return response


@app.route('/aReports', methods=['GET'])
def aReports():
    username = CASClient().authenticate()
    database = Database()

    reports = database.getReports()
    html = render_template('aReports.html',
                            username=username,
                            reports=reports,
                            database=database)
    response = make_response(html)
    return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
