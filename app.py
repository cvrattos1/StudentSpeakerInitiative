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

app = Flask(__name__)

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

cloudinary.config(cloud_name='dqp1yoed2',
                  api_key='129874246392789',
                  api_secret='wovIZCIrF_S2yEE5mM1b2ha5lao')


def filllist(username, database, request):
    finallist = []

    if request == "endorsement":
        speakers = database.getSpeakers()
        for speaker in speakers:
            speakerid = speaker
            name = database.getSpeakerFirstName(speaker) + " " + database.getSpeakerLastName(speaker)
            description = database.getSpeakerDescription(speaker)
            endorsement = database.hasEndorsed(username, speaker)
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
    remaining = allowance - database.usedEndorsements(username)
    html = render_template('sEndorse.html',
                           username=username,
                           endorsementlist=endorsementlist,
                           remaining=remaining,
                           allowance=allowance)
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

    cycle = database.getCycle()
    if cycle is None:
        html = render_template('snotNom.html',
                               username=username,
                               exists=0)
        response = make_response(html)

        return response

    else:
        remaining = database.remainingNominations(username)
        voting = database.getCycle().getDateVoting() <= datetime.date.today()
        print(voting)

        if not voting:
            if remaining == 0:
                html = render_template('sNoNom.html',
                                       username=username)
            else:
                errorMsg = request.args.get('errorMsg')
                if errorMsg is None:
                    errorMsg = ''
                html = render_template('sNom.html',
                                       username=username,
                                       errorMsg=errorMsg,
                                       cycle=cycle,
                                       remaining=remaining)

            response = make_response(html)
            return response
        else:
            html = render_template('snotNom.html',
                                   username=username,
                                   exists=1)
            response = make_response(html)
            return response


@app.route('/nominate_flask', methods=['POST'])
def nominate_flask():
    username = CASClient().authenticate()
    database = Database()

    name = request.form['name']
    descrip = request.form['descrip']
    links = request.form['links']
    img = request.files['file']
    result = Cloud.uploader.upload(img, use_filename='true', filename=img.filename, folder='SSI')
    imglink = result['secure_url']

    if name == '' or descrip == '':
        errorMsg = "None of the fields can be empty."
        return redirect(url_for('sNom',
                                errorMsg=errorMsg))

    if not database.remainingNominations(username) == 0:
        cycle = database.getCycle().getName()
        database.nominate(username, cycle, name, descrip, links, imglink)

    response = renderendorse(username, database)

    return response


@app.route('/new_cycle')
def new_cycle():
    username = CASClient().authenticate()
    database = Database()

    if (request.args.get('nominatenum') == '' or request.args.get('endorsenum') == '' or
            request.args.get('votenum') == '' or request.args.get('votingdate') == '' or
            request.args.get('threshold') == '' or request.args.get('cname') == ''):
        errorMsg = "None of the fields can be empty."
        return redirect(url_for('new_cycle',
                                errorMsg=errorMsg,
                                username=username))

    name = request.args.get('cname')
    votingdate = request.args.get('votingdate')
    enddate = request.args.get('enddate')
    threshold = request.args.get('threshold')
    datecreated = datetime.datetime.now().strftime("%x")
    admin = request.args.get('admin')

    if (request.args.get('nominatenum') == "limited"):
        nomination_count = request.args.get('nominatetext')
    else:
        nomination_count = 2147483647

    if request.args.get('endorsenum') == "limited":
        endorse_count = request.args.get('endorsetext')
    else:
        endorse_count = 2147483647

    if request.args.get('votenum') == "limited":
        vote_count = request.args.get('votetext')
    else:
        vote_count = 2147483647

    database.createCycle(name, datecreated, admin, nomination_count, endorse_count, vote_count, threshold,
                         votingdate, enddate)

    rolloverNom = request.args.get('rolloverNom')
    rolloverEnd = request.args.get('rolloverEnd')
    rolloverVot = request.args.get('rolloverVot')

    cycle = database.getCycle()
    if cycle is None:
        exists = 0
    else:
        exists = 1

    html = render_template('aHome.html',
                           username=username,
                           cycle=cycle,
                           exists=exists)
    response = make_response(html)
    return response


@app.route('/endorse_flask')
def endorse_flask():
    username = CASClient().authenticate()
    database = Database()
    speakerid = request.args.get('speakerid')
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


@app.route('/reset_flask')
def reset_flask():
    username = CASClient().authenticate()
    database = Database()

    html = render_template('aCreateCycle.html',
                           username=username,
                           )
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
    cycle = database.getCycle()
    if cycle is None:
        html = render_template('snotEndorse.html',
                               username=username,
                               cycle=cycle,
                               exists=0
                               )
        response = make_response(html)
        return response
    else:
        voting = database.getCycle().getDateVoting() <= datetime.date.today()
        student = database.getStudent(username)
        if voting:
            html = render_template('snotEndorse.html',
                                   username=username,
                                   cycle=cycle,
                                   exists=1,
                                   )
            response = make_response(html)
            return response
        elif student is not None and student.getEndorsements() == 1:
            html = render_template('snotEndorse.html',
                                   username=username,
                                   cycle=cycle,
                                   exists=2,
                                   )
            response = make_response(html)
            return response
        else:
            speakers = database.getSpeakers()
            html = render_template('sEndorse.html',
                                   username=username,
                                   cycle=cycle,
                                   speakers=speakers
                                   )
            response = make_response(html)
            return response


@app.route('/sVote', methods=['GET'])
def sVote():
    username = CASClient().authenticate()
    database = Database()

    cycle = database.getCycle()
    if cycle is None:
        html = render_template('snotVote.html',
                               username=username,
                               cycle=cycle,
                               exists=0
                               )
        response = make_response(html)
        return response
    else:
        voting = database.getCycle().getDateVoting() <= datetime.date.today()
        student = database.getStudent(username)
        if not voting:
            html = render_template('snotVote.html',
                                   username=username,
                                   cycle=cycle,
                                   exists=1
                                   )
            response = make_response(html)
            return response

        elif student is not None and student.getVotes() == 1:
            html = render_template('snotVote.html',
                                   username=username,
                                   cycle=cycle,
                                   exists=2
                                   )
            response = make_response(html)
            return response
        else:
            speakers = database.getEndorsed(cycle.getThreshold())
            html = render_template('sVote.html',
                                   username=username,
                                   cycle=cycle,
                                   speakers=speakers
                                   )
            response = make_response(html)

            return response
    votingperiod = database.votePeriod()
    if votingperiod:
        if database.hasVoted(username):
            html = render_template('salreadyVote.html',
                                   username=username)
            response = make_response(html)
        else:
            votinglist = filllist(username, database, "voting")
            shuffle(votinglist)
            html = render_template('sVote.html',
                                   username=username,
                                   votinglist=votinglist)
            response = make_response(html)
    else:
        cycle = database.getCycleInfo()
        if not cycle:
            cycle = "TBD"
            exists = 0
        else:
            cycle = cycle[0][2]
            exists = 1
        html = render_template('snotVote.html',
                               username=username,
                               info=cycle,
                               exists=exists)
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
