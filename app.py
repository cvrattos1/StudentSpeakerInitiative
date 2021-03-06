# app.py
from random import shuffle
from urllib.parse import urlparse

from flask import Flask, request, jsonify
from flask import make_response, redirect, render_template, url_for
from CASClient import CASClient
from database import Database
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
from datetime import date, timedelta
import pustatus

from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from userAccount import userAccount

UNLIMITED_VALUE = 2147483647

login_manager = LoginManager()

app = Flask(__name__)

login_manager.init_app(app)

login_manager.login_view = "/index"

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

# deletes the image associated with a particular speakid from cloudinary. Returns a success/failure status
def deleteImage(imagelink):
    parsed = urlparse(imagelink)
    result = parsed.path.split('/')[6]
    result = 'SSI/' + result
    result = result[:-4]
    deleted = Cloud.uploader.destroy(result)
    return deleted

def filllist(username, database, request):
    finallist = []

    if request == "endorsement":
        finallist = database.getSpeakers()

    elif request == "voting":
        finallist = database.getEndorsed(1)

    return finallist

def cyclevalidation(cycle):
    database = Database()
    if cycle.getName():
        if cycle.getDateEnd() <= datetime.date.today():
          nominating = False
          endorsing = False
          voting = False
          results = False

        elif cycle.getDateResults() <= datetime.date.today():
          nominating = False
          endorsing = False
          voting = False
          results = True

        elif cycle.getDateVoting() <= datetime.date.today():
          nominating = False
          endorsing = False
          voting = True
          results = False

        elif cycle.getDateEndorse() <= datetime.date.today():
          nominating = False
          endorsing = True
          voting = False
          results = False

        elif cycle.getDateNom() <= datetime.date.today():
          nominating = True
          endorsing = False
          voting = False
          results = False

        else:
          nominating = False
          endorsing = False
          voting = False
          results = False
    else:
        nominating = False
        endorsing = False
        voting = False
        results = False


    validation = {"nominating":nominating,"endorsing":endorsing, "voting": voting, "results": results }

    if not validation["nominating"]:
        database.deleteReports()
    return validation

def uservalidation(username, database):
    special = database.getSpecial(username)
    if special:
        student = database.getStudent(username)
        if not student:
            database.makeStudent(username)
        faculty = database.getFaculty(username)
        if not faculty:
            database.makeFaculty(username)
        return "special"
    admin = database.adminAuthenticate(username)
    if admin:
        return "admin"
    undergrad = pustatus.isUndergraduate(ldapserver, username)
    if undergrad:
        student = database.getStudent(username)
        if not student:
            database.makeStudent(username)
        return "undergraduates"
    fac = pustatus.isFaculty(ldapserver, username)
    if fac:
        faculty = database.getFaculty(username)
        if not faculty:
            database.makeFaculty(username)
        return "faculty"
    return "other"



def checkuser(role, pageType):

    if role == pageType:
        return True

    elif role == "special":
        return True

    else:
        return False

def loginfail(username, pageType):
    html = render_template('loginfail.html',
                                   username=username,
                                   pageType= pageType)
    response = make_response(html)

    return response


@login_manager.user_loader
def load_user(user_id):
    try:
        username = CASClient().authenticate()
        if user_id != username:
            return None
        database = Database()
        role = uservalidation(user_id, database)
        return userAccount(user_id, role)
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
    return redirect('/')


@app.route('/sHome', methods=['GET', 'POST'])
def sHome():
    username = CASClient().authenticate()
    try:
        pageType = "undergraduates"
        database = Database()
        role = uservalidation(username, database)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            useraccount = userAccount(username, role)
            login_user(useraccount)
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            html = render_template('sHome.html',
                                   username=username,
                                   cycle=cycle,
                                   validation=validation
                                   )
            response = make_response(html)

    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
    return response

@app.route('/sFAQ', methods=['GET'])
@login_required
def sFAQ():
    username = current_user.id
    try:
        pageType = "undergraduates"
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            html = render_template('sFAQ.html',
                                   username=username,
                                   cycle=cycle,
                                   validation=validation
                                   )
            response = make_response(html)

    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
    return response

@app.route('/fHome', methods=['GET', 'POST'])
def fHome():
    username = CASClient().authenticate()
    try:
        pageType = "faculty"
        database = Database()
        role = uservalidation(username, database)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            useraccount = userAccount(username, role)
            login_user(useraccount)
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            faculty = database.getFaculty(username)
            if faculty:
                hasapproved = faculty.getPromotions()
            else:
                hasapproved = 0
            html = render_template('fHome.html',
                                   username=username,
                                   cycle=cycle,
                                   validation=validation,
                                   hasapproved=hasapproved
                                   )
            response = make_response(html)

    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
    return response


@app.route('/fResults', methods=['GET'])
@login_required
def fResults():
    try:
        pageType = "faculty"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)

            approvedconversations = database.getConversations(1)

            html = render_template('fResults.html',
                                   username=username,
                                   approvedconversations = approvedconversations,
                                   validation=validation,
                                   cycle=cycle
                                   )
            response = make_response(html)

            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response



@app.route('/sNom')
@login_required
def sNom():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:
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


            response = make_response(html)
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/nominate_flask', methods=['POST'])
@login_required
def nominate_flask():
    pageType = "undergraduates"
    database = Database()
    username = current_user.id
    check = checkuser(current_user.role, pageType)
    if not check:
        return loginfail(username, pageType)

    else:
        cycle = database.getCycle()
        remaining = database.remainingNominations(username)
        validation = cyclevalidation(cycle)
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

        if remaining:
            # upload image to cloudinary
            result = Cloud.uploader.upload(argdict['Image'], use_filename='true', filename=(argdict['Image'].filename), folder='SSI', width=400, height=500, crop="limit")
            imglink = result['secure_url']

            # store speaker info in database
            database.nominate(username,
                              cycle.getName(),
                              argdict['Name of Nomination'],
                              argdict['Description'],
                              argdict['Link to works'],
                              imglink)

            # send confirmation email
            try:
                recipient = username[:-1] + "@princeton.edu"
                msg = Message("Hello",sender="ssidev@princeton.edu",recipients=[recipient])
                msg.body = "Dear Student,\n\nYour nomination of " + argdict['Name of Nomination'] + " has been submitted. Thank you for your input.\n\nSincerely,\nThe Students' Speaker Initiative"
                msg.subject = "Students' Speakers Initiative Nomination Confirmation"
                mail.send(msg)
                print('Mail sent to ' + recipient)
            except Exception as e:
                print(str(e))
                print(username[:-1] + "@princeton.edu")


        return redirect('sEndorse')


@app.route('/new_cycle')
@login_required
def new_cycle():
    try:
        username = current_user.id
        database = Database()

        argdict = {"Name of Voting Cycle":request.args.get('cname'),
                   "Number of Nominations":request.args.get('nominatenum'),
                   "Number of Endorsements":request.args.get('endorsenum'),
                   "Number of Votes":request.args.get('votenum'),
                   "Endorsement Threshold":request.args.get('endorsethresh'),
                   "Nomination Date Begins":request.args.get('nomdate'),
                   "Endsorsement Date Begins":request.args.get('endorsedate'),
                   "Voting Date Begins":request.args.get('votingdate'),
                   "Result Date Begins": request.args.get('resultsdate'),
                   "End Date": request.args.get('enddate')
                   }

        datecreated = datetime.datetime.now().strftime("%x")
        admin = request.args.get('admin')

        argerror = False
        wrongarg = []
        for key, value in argdict.items():
            if not value :
                return redirect('aCreateCycle')

        if (argdict["Nomination Date Begins"] >= argdict["Endsorsement Date Begins"]
                or argdict["Endsorsement Date Begins"] >= argdict["Voting Date Begins"]
                or argdict["Voting Date Begins"] >= argdict["Result Date Begins"]
                or argdict["Result Date Begins"] >= argdict["End Date"]):
            return redirect('aCreateCycle')

        admin = request.args.get('admin')

        if (argdict['Number of Nominations'] == "limited"):
            nomination_count = request.args.get('nominatetext')
            if int(nomination_count) < 1:
                return redirect('aCreateCycle')
        else:
            nomination_count = UNLIMITED_VALUE

        if (argdict['Number of Endorsements'] == "limited"):
            endorse_count = request.args.get('endorsetext')
            if int(endorse_count) < 1:
                return redirect('aCreateCycle')
        else:
            endorse_count = UNLIMITED_VALUE

        if (argdict['Number of Votes'] == "limited"):
            vote_count = request.args.get('votetext')
            if int(vote_count) < 1:
                return redirect('aCreateCycle')
        else:
            vote_count = UNLIMITED_VALUE

        rolloverThresh = request.args.get('rolloverthresh')
        rolloverNom = request.args.get('rollovernom')
        rolloverEnd = request.args.get('rolloverend')
        rolloverVot = request.args.get('rollovervot')

        database.adjustDatabase(rolloverNom, rolloverEnd, rolloverVot, rolloverThresh)
        today = datetime.datetime.today()
        formatEndDate = datetime.datetime.strptime(argdict["End Date"], '%Y-%m-%d').strftime('%b %d, %Y')
        database.addLog(today, username, 2, formatEndDate)

        database.createCycle(name=argdict["Name of Voting Cycle"],
                             datecreated=datecreated,
                             admin=admin,
                             nominatenum=nomination_count,
                             endorsenum=endorse_count,
                             votenum=vote_count,
                             endorsethresh=argdict["Endorsement Threshold"],
                             rollthresh=rolloverThresh,
                             nomdate=argdict["Nomination Date Begins"],
                             endorsedate=argdict["Endsorsement Date Begins"],
                             votingdate=argdict["Voting Date Begins"],
                             resultsdate=argdict["Result Date Begins"],
                             enddate=argdict["End Date"])

        return redirect('aHome')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/nextstep_flask', methods=['POST'])
@login_required
def nextstep_flask():
    try:
        username = current_user.id
        database = Database()
        cycle = database.getCycle()

        validation = cyclevalidation(cycle)
        if (validation['nominating']):
            nomdate = datetime.date.today() - timedelta(days=1)
            endorsedate = datetime.date.today()
            votingdate = cycle.getDateVoting();
            resultsdate = cycle.getDateResults();
            enddate = cycle.getDateEnd();
        elif (validation['endorsing']):
            nomdate = datetime.date.today() - timedelta(days=2)
            endorsedate = datetime.date.today() - timedelta(days=1)
            votingdate = datetime.date.today();
            resultsdate = cycle.getDateResults();
            enddate = cycle.getDateEnd();
        elif (validation['voting']):
            nomdate = datetime.date.today() - timedelta(days=3)
            endorsedate = datetime.date.today() - timedelta(days=2)
            votingdate = datetime.date.today() - timedelta(days=1)
            resultsdate = datetime.date.today();
            enddate = cycle.getDateEnd();
        elif (validation['results']):
            nomdate = datetime.date.today() - timedelta(days=4)
            endorsedate = datetime.date.today() - timedelta(days=3)
            votingdate = datetime.date.today() - timedelta(days=2)
            resultsdate = datetime.date.today() - timedelta(days=1)
            enddate = datetime.date.today();
        else: return redirect('aHome')

        database.adjustDatabase(True, True, True, cycle.getRolloverThreshold())

        database.createCycle(name=cycle.getName(),
                             datecreated=cycle.getDateCreated(),
                             admin=cycle.getAdmin(),
                             nominatenum=cycle.getNominateNum(),
                             endorsenum=cycle.getEndorseNum(),
                             votenum=cycle.getVoteNum(),
                             endorsethresh=cycle.getThreshold(),
                             rollthresh=cycle.getRolloverThreshold(),
                             nomdate=nomdate,
                             endorsedate=endorsedate,
                             votingdate=votingdate,
                             resultsdate=resultsdate,
                             enddate=enddate)
        return redirect('aHome')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/prevstep_flask', methods=['POST'])
@login_required
def prevstep_flask():
    try:
        username = current_user.id
        database = Database()
        cycle = database.getCycle()

        validation = cyclevalidation(cycle)
        if (validation['nominating']): return redirect('aHome')
        elif (validation['endorsing']):
            nomdate = datetime.date.today()
            endorsedate = datetime.date.today() + timedelta(days=1)
            votingdate = datetime.date.today() + timedelta(days=2)
            resultsdate = datetime.date.today() + timedelta(days=3)
            enddate = datetime.date.today() + timedelta(days=4)
        elif (validation['voting']):
            nomdate = cycle.getDateNom()
            endorsedate = datetime.date.today()
            votingdate = datetime.date.today() + timedelta(days=1)
            resultsdate = datetime.date.today() + timedelta(days=2)
            enddate = datetime.date.today() + timedelta(days=3)
        elif (validation['results']):
            nomdate = cycle.getDateNom()
            endorsedate = cycle.getDateEndorse()
            votingdate = datetime.date.today()
            resultsdate = datetime.date.today() + timedelta(days=1)
            enddate = datetime.date.today() + timedelta(days=2)
        else:
            nomdate = cycle.getDateNom()
            endorsedate = cycle.getDateEndorse()
            votingdate = cycle.getDateVoting()
            resultsdate = datetime.date.today()
            enddate = datetime.date.today() + timedelta(days=1)

        database.adjustDatabase(True, True, True, cycle.getRolloverThreshold())

        database.createCycle(name=cycle.getName(),
                             datecreated=cycle.getDateCreated(),
                             admin=cycle.getAdmin(),
                             nominatenum=cycle.getNominateNum(),
                             endorsenum=cycle.getEndorseNum(),
                             votenum=cycle.getVoteNum(),
                             endorsethresh=cycle.getThreshold(),
                             rollthresh=cycle.getRolloverThreshold(),
                             nomdate=nomdate,
                             endorsedate=endorsedate,
                             votingdate=votingdate,
                             resultsdate=resultsdate,
                             enddate=enddate)
        return redirect('aHome')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/endorse_flask', methods=['POST'])
@login_required
def endorse_flask():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
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
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/vote_flask', methods=['POST'])
@login_required
def vote_flask():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            voted = request.form.getlist('number')
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

                if count > int(cycle.getVoteNum()) or error == True:
                    return redirect('sVote')

            for i in range(len(voted)):
                if voted[i] != '':
                    database.vote(username, speakids[i], voted[i])
            return redirect('sVote')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/flag_flask')
@login_required
def flag_flask():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            reason = request.args.get('reason')
            speakerid = request.args.get('speakerid')

            database.flag(username, speakerid, reason)
            try:
                recipient = username[:-1] + "@princeton.edu"
                msg = Message("Hello",sender="ssidev@princeton.edu",recipients=[recipient])
                msg.body = "Dear Student,\n\nYour flag request has been submitted to the Students' Speaker Initiative comittee for review. Thank you for your feedback.\n\nSincerely,\nThe Students' Speaker Initiative"
                msg.subject = "Students' Speakers Initiative Flag"
                mail.send(msg)
                print('Mail sent to ' + recipient)
            except Exception as e:
                print(str(e))
                print(username[:-1] + "@princeton.edu")

            return redirect('sEndorse')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/remove_nomination')
@login_required
def remove_nomination():
    try:
        username = current_user.id
        database = Database()
        speakerid = request.args.get('speakerid')
        today = datetime.datetime.today()
        speakerinfo = database.getSpeaker(speakerid)    # returns Speaker object
        database.addLog(today, username, 4, speakerinfo.getName())

        imagelink = database.getImage(speakerid)
        imagelink = imagelink[0][0]
        deleteImage(imagelink)

        database.removeNomination(speakerid)

        return redirect('aReports')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/dismiss_flag')
@login_required
def dismiss_flag():
    try:
        username = current_user.id
        database = Database()

        speakerid = request.args.get('speakerid')
        database.dismissFlag(speakerid)

        today = datetime.datetime.today()
        speakerinfo = database.getSpeaker(speakerid)
        database.addLog(today, username, 3, speakerinfo.getName())

        return redirect('aReports')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/ssearch', methods=['GET'])
@login_required
def ssearch():
    pageType = "undergraduates"
    database = Database()
    username = current_user.id
    check = checkuser(current_user.role, pageType)
    if not check:
        return loginfail(username, pageType)

    else:
        try:
            # Name is the name that the user types in the search bar
            name = request.args.get('name')
            if name is None:
                name = ''

            speakers = database.searchEndorsements(name, username)
           
            if name == '':
                shuffle(speakers)
            html = render_template('sresults.html', speakers=speakers)
            response = make_response(html)
        except Exception as e:
            print(e, file=stderr)
            html = "A search related error occurred"
            response = make_response(html)
        return response

@app.route('/adminsearch', methods=['GET'])
@login_required
def adminsearch():
    try:
        name = request.args.get('name')
        if name is None:
            name = ''
        
        database = Database()
        info = database.searchAdminLogs(name)
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
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:

            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            student = database.getStudent(username)
            if student:
                hasendorsed = student.getEndorsements()
            else:
                hasendorsed = 0
            speakers = database.getSpeakers()
            shuffle(speakers)
            html = render_template('sEndorse.html',
                                   username= username,
                                   cycle= cycle,
                                   speakers= speakers,
                                   validation = validation,
                                   hasendorsed = hasendorsed
                                   )
            response = make_response(html)

            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/sVote', methods=['GET'])
@login_required
def sVote():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:

            cycle = database.getCycle()
            user = database.getStudent(username)
            validation = cyclevalidation(cycle)

            if cycle.getName():
                speakers = database.getEndorsed(cycle.getThreshold())
                if validation['results']:
                    speakers.sort(key=lambda x: x.getVotes(), reverse = True )
                else:
                    shuffle(speakers)
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
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/scNom')
@login_required
def scNom():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            if cycle.getName():
                remaining = database.remainingccNominations(username)
            else:
                remaining=None;
            validation = cyclevalidation(cycle)
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
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/ccnominate_flask', methods=['POST'])
@login_required
def ccnominate_flask():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:

            cycle = database.getCycle()
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

            emailString = ''
            count = 1
            for name in names:
                emailString = emailString + "Speaker" + str(count) + ": " + name + "\n"
                count = count + 1

            if remaining:
                # nominate conversation
                database.ccnominate(username,
                                cycle.getName(),
                                conzip)

                # send confirmation email
                try:
                    recipient = username[:-1] + "@princeton.edu"
                    msg = Message("Hello",sender="ssidev@princeton.edu",recipients=[recipient])
                    msg.body = "Dear Student,\n\nYour panel nomination has been submitted. Thank you for your input.\n\nPanel:\n" + emailString + "\nSincerely,\nThe Students' Speaker Initiative"
                    msg.subject = "Students' Speakers Initiative Nomination Confirmation"
                    mail.send(msg)
                    print('Mail sent to ' + recipient)
                except Exception as e:
                    print(str(e))
                    print(username[:-1] + "@princeton.edu")

        return redirect('scEndorse')

    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response



@app.route('/ccendorse_flask', methods=['POST'])
@login_required
def ccendorse_flask():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            cyclevalidation(cycle)

            endorsed = request.form.get('list')
            endorsed = endorsed.split(',')

            student = database.getStudent(username)
            if student.getccEndorsements():
                return redirect('sHome')
            if cycle.getEndorseNum() != 'unlimited':
                if len(endorsed) > int(cycle.getEndorseNum()):
                    #some error
                    return redirect('scEndorse')

            for converseid in endorsed:
                database.ccendorse(username, converseid, 1)

            return redirect('scEndorse')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response



@app.route('/fapprove_flask', methods=['POST'])
@login_required
def fapprove_flask():
    try:
        pageType = "faculty"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            cyclevalidation(cycle)

            approved = request.form['conversationid']
            conversation = database.getConversation(approved)
            already = conversation.getFaculty()
            faculty = database.getFaculty(username)

            if faculty.getPromotions():
                return redirect('fHome')

            else:
                if already != "0":
                      # return ('', 204)
                    return redirect('fHome')
                else:
                    database.fpromote(username, approved)
                    return redirect('fHome')
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response



@app.route('/ccvote_flask' , methods=['POST'])
@login_required
def ccvote_flask():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            cyclevalidation(cycle)
            voted = request.form.getlist('number')
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
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/scEndorse', methods=['GET'])
@login_required
def scEndorse():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            student = database.getStudent(username)
            if student:
                hasendorsed = student.getccEndorsements()
            else:
                hasendorsed = 0
            conversations = database.getConversations(1)
            finalconversations = []
            if not validation["nominating"]:
                for conversation in conversations:
                    if ((conversation.getNetid()) != (username.strip())):
                        finalconversations.append(conversation)
            else:
                finalconversations = conversations
            shuffle(finalconversations)
            html = render_template('scEndorse.html',
                                   username= username,
                                   cycle= cycle,
                                   conversations = finalconversations,
                                   validation = validation,
                                   hasendorsed = hasendorsed
                                   )
            response = make_response(html)

            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/fApprove', methods=['GET'])
@login_required
def fApprove():
    try:
        pageType = "faculty"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:
            database = Database()
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            faculty = database.getFaculty(username)
            if faculty:
                hasapproved = faculty.getPromotions()
            else:
                hasapproved = 0
            conversations = database.getConversations(0)
            html = render_template('fApprove.html',
                                   username= username,
                                   cycle= cycle,
                                   conversations = conversations,
                                   validation = validation,
                                   hasapproved = hasapproved
                                   )
            response = make_response(html)

            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/scVote', methods=['GET'])
@login_required
def scVote():
    try:
        pageType = "undergraduates"
        database = Database()
        username = current_user.id
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)

        else:

            cycle = database.getCycle()
            student = database.getStudent(username)
            validation = cyclevalidation(cycle)

            if cycle.getName():
                conversations = database.getccEndorsed(cycle.getThreshold())
                if validation['results']:
                    conversations.sort(key=lambda x: x.getVotes(), reverse = True )
                else:
                    shuffle(conversations)
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
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/sAdminLogs', methods=['GET'])
@login_required
def sAdminLogs(): 
    try:
        username = current_user.id
        database = Database()
        info = database.returnAdminLogs()
        admins = database.returnAdmins()
        validation = cyclevalidation(database.getCycle())

        html = render_template('sAdminLogs.html',
                                admins=admins,
                                info=info,
                                validation=validation)
        response = make_response(html)
        return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


# Should add another layer of authentication
@app.route('/aHome', methods=['GET'])
def aHome():
    username = CASClient().authenticate()
    try:
        pageType = "admin"
        database = Database()
        role = uservalidation(username, database)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:
            useraccount = userAccount(username, "admin")
            login_user(useraccount)
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            admins = database.returnAdmins()
            html = render_template('aHome.html',
                                   username=username,
                                   admins=admins,
                                   cycle=cycle,
                                   validation=validation
                                   )
            response = make_response(html)
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)

    return response


@app.route('/aNoms', methods=['GET'])
@login_required
def aNoms():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
    
            speakers = database.getSpeakers()
            html = render_template('aNoms.html',
                                   username=username,
                                   speakers=speakers,
                                   validation=validation,
                                   cycle=cycle
                                   )
            response = make_response(html)
    
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/acNoms', methods=['GET'])
@login_required
def acNoms():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:

            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
    
            conversations = database.getConversations(0)
            approvedconversations = database.getConversations(1)
    
            html = render_template('acNoms.html',
                                   username=username,
                                   conversations = conversations,
                                   approvedconversations = approvedconversations,
                                   cycle=cycle,
                                   validation=validation
                                   )
            response = make_response(html)
    
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/acVotes', methods=['GET'])
@login_required
def acVotes():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:

            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
    
            approvedconversations = database.getccEndorsed(cycle.getThreshold())
            if validation['results']:
                        approvedconversations.sort(key=lambda x: x.getVotes(), reverse = True )
            html = render_template('acVotes.html',
                                   username=username,
                                   approvedconversations = approvedconversations,
                                   validation=validation,
                                   cycle=cycle
                                   )
            response = make_response(html)
    
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/aVotes', methods=['GET'])
@login_required
def aVotes():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:

            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
            speakers = database.getEndorsed(cycle.getThreshold())
            if validation['results']:
                speakers.sort(key=lambda x: x.getVotes(), reverse = True )
            html = render_template('aVotes.html',
                                   username=username,
                                   speakers=speakers,
                                   cycle=cycle,
                                   validation=validation
                                   )
            response = make_response(html)
    
    
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/aCreateCycle')
@login_required
def aCreateCycle_flask():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:

            html = render_template('aCreateCycle.html',
                                   username=username,
                                   )
            response = make_response(html)
    
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response


@app.route('/aReports', methods=['GET'])
@login_required
def aReports():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:
            cycle = database.getCycle()
            validation = cyclevalidation(cycle)
    
            reports = database.getReports()
            speakers = []
            for report in reports:
                speakers.append(database.getSpeaker(report.getSpeakid()))
    
            html = render_template('aReports.html',
                                   username=username,
                                   cycle=cycle,
                                   validation=validation,
                                   reports=reports,
                                   speakers=speakers,
                                   length=len(speakers)
                                   )
            response = make_response(html)

            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/addAdmin', methods=['GET'])
@login_required
def addAdmin():
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:
            newAdmin = request.args.get('newAdmin')
            if database.adminAuthenticate(newAdmin) != 1:  # can't double add
                database.addAdmin(newAdmin)
                today = datetime.datetime.today()   # add action to DB
                database.addLog(today, username, 0, newAdmin)
            return redirect(url_for('aHome'))
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/removeAdmin', methods=['GET'])
@login_required
def removeAdmin():
    try:
        oldAdmin = request.args.get('oldAdmin')
        username = current_user.id
        database = Database()
        if database.returnCount('admin') != 1 and oldAdmin != "":  # can't delete last admin or empty admin
            database.removeAdmin(oldAdmin)
            today = datetime.datetime.today()                       # add action to DB
            database.addLog(today, username, 1, oldAdmin)
        return redirect(url_for('aHome'))
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

@app.route('/aAdminLogs', methods=['GET'])
@login_required
def aAdminLogs(): 
    try:
        pageType = "admin"
        username = current_user.id
        database = Database()
        check = checkuser(current_user.role, pageType)
        if not check:
            return loginfail(username, pageType)
        else:
            info = database.returnAdminLogs()
            admins = database.returnAdmins()
            html = render_template('aAdminLogs.html',
                                    admins=admins,
                                    info=info)
            response = make_response(html)
            return response
    except Exception as e:
        errorDate = datetime.datetime.today()
        print("ERROR: [" + str(e) + "] occured at " + str(errorDate), file=stderr)
        html = render_template('error.html')
        response = make_response(html)
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)

