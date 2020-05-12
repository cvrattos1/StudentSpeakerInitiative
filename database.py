#!usr/bin/env python

# ---------------------------------------------------------------------
# database.py
# Author: Caroline di Vittorio
# ---------------------------------------------------------------------

import os
import psycopg2

from student import Student
from speaker import Speaker
from faculty import Faculty
from cycle import Cycle
from report import Report
from conversation import Conversation
import cloudinary.uploader
import json

UNLIMITED_VALUE = 2147483647

cloudinary.config(cloud_name=os.environ['CLOUD_NAME'],
                  api_key=os.environ['API_KEY'],
                  api_secret=os.environ['API_SECRET'])


# ----------------------------------------------------------------------
# Prepares the values to be inserted into database such that they
# handle single quotes within the key
# ----------------------------------------------------------------------
def prep(text):
    prepped = ''
    for i in range(len(text)):
        if text[i] == '\'':
            prepped = prepped + '\''
        prepped = prepped + text[i]
    return prepped


class Database:
    # ----------------------------------------------------------------------
    # connect to the database and execute query; return result of
    # query, if there is one.
    # ----------------------------------------------------------------------
    def connectDB(self, query):
        try:
            # DATABASE_URL = os.environ['DATABASE_URL']
            DATABASE_URL = 'postgres://fhfqbhbbxmzxjr:4258130a81cde0e835e3bb78d4e93e5660840682f5a140975f26a900a42a6067@ec2-23-22-156-110.compute-1.amazonaws.com:5432/dtc2bl3kqgkv'

            connection = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = connection.cursor()

            cursor.execute(query)
            connection.commit()

            elements = cursor.fetchall()

            cursor.close()
            connection.close()

            return elements

        except Exception as e:
            print(e)
            return []

    # ---------------------------------------------------------------------
    # returns the information about the student with netid as a Student
    # object, or None if does not exist
    # ----------------------------------------------------------------------
    def getStudent(self, netid):
        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"

        result = Database.connectDB(self, query)

        if not result:
            return None
        student = Student(netid, result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6])
        return student

    # ----------------------------------------------------------------------
    # returns the information about the faculty with netid as Faculty object,
    # or None if it does not exist.
    # ----------------------------------------------------------------------
    def getFaculty(self, netid):
        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM faculty WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"

        result = Database.connectDB(self, query)

        if not result:
            return None
        faculty = Faculty(netid, result[0][1])
        return faculty

    # ----------------------------------------------------------------------
    def getSpecial(self, netid):
        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM special WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"

        result = Database.connectDB(self, query)

        if not result:
            return None

        return True

    # ----------------------------------------------------------------------
    # Creates a new student in the database with netid; sets all parameters
    # to 0
    # ----------------------------------------------------------------------
    def makeStudent(self, netid):
        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"
        result = Database.connectDB(self, query)
        if result:
            raise Exception("Already exists.")

        query = "PREPARE stmt(text) AS " \
                "INSERT INTO students VALUES($1, 0, 0, 0, 0, 0, 0);" \
                "EXECUTE stmt('" + netid.strip() + "');"

        Database.connectDB(self, query)

    # ----------------------------------------------------------------------
    # Creates a new faculty inside the database with netid 0; sets all
    # parameters to 0
    # ----------------------------------------------------------------------
    def makeFaculty(self, netid):

        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM faculty WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"
        result = Database.connectDB(self, query)
        if result:
            raise Exception("Already exists.")

        query = "PREPARE stmt(text) AS " \
                "INSERT INTO faculty VALUES($1, 0);" \
                "EXECUTE stmt('" + netid.strip() + "');"
        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # returns the information about the speaker with speakid as a Speaker
    # object, or None if does not exist
    # ---------------------------------------------------------------------
    def getSpeaker(self, speakid):

        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM speakers WHERE speakid = $1;" \
                "EXECUTE stmt('" + str(speakid) + "');"

        result = Database.connectDB(self, query)

        if not result:
            return None
        speaker = Speaker(speakid, result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6],
                          result[0][7], result[0][8])
        return speaker

    # ---------------------------------------------------------------------
    # Returns the current cycle as a Cycle object
    # ---------------------------------------------------------------------
    def getCycle(self):

        query = "SELECT * from cycle"
        result = Database.connectDB(self, query)

        if not result:
            return Cycle(None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        else:
            return Cycle(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5],
                         result[0][6],
                         result[0][7], result[0][8], result[0][9], result[0][10], result[0][11], result[0][12],
                         result[0][13])

    # ---------------------------------------------------------------------
    # returns as an integer the number of endorsements remaining for the
    # student with netid netid
    # ---------------------------------------------------------------------
    def hasEndorsed(self, netid):

        query = "PREPARE stmt(text) AS " \
                "SELECT endorsements FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid + "');"

        endorsements = Database.connectDB(self, query)
        if not endorsements:
            return 0
        else:
            return endorsements

    # ---------------------------------------------------------------------
    # returns as an integer the number of endorsements remaining for the
    # student with netid netid
    # ---------------------------------------------------------------------
    def remainingNominations(self, netid):

        query = "PREPARE stmt(text) AS " \
                "SELECT nominations FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"

        noms = Database.connectDB(self, query)
        if noms:
            nominations = noms[0][0]
        else:
            nominations = 0

        query = "SELECT nominatenum FROM cycle"
        allowance = Database.connectDB(self, query)[0][0]

        if allowance == UNLIMITED_VALUE:
            return "unlimited"
        else:
            return allowance - nominations

    # ---------------------------------------------------------------------
    # returns as an integer the number of ccendorsements remaining for the
    # student with netid netid
    # ---------------------------------------------------------------------
    def remainingccNominations(self, netid):

        query = "PREPARE stmt(text) AS " \
                "SELECT ccnominations FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"

        ccnoms = Database.connectDB(self, query)
        if ccnoms[0][0]:
            ccnominations = ccnoms[0][0]
        else:
            ccnominations = 0

        query = "SELECT nominatenum FROM cycle"
        allowance = Database.connectDB(self, query)[0][0]

        if allowance == UNLIMITED_VALUE:
            return "unlimited"
        else:
            return allowance - ccnominations

    # ---------------------------------------------------------------------
    # returns as an integer the number of votes used by the
    # student with netid netid
    # ---------------------------------------------------------------------
    def hasVoted(self, netid):

        query = "PREPARE stmt(text) AS " \
                "SELECT votes FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid + "');"

        votes = Database.connectDB(self, query)
        if not votes:
            return 0
        else:
            return votes

    # ---------------------------------------------------------------------
    # returns as an integer the number of endorsements that the student
    # with netid netid has currently used
    # ---------------------------------------------------------------------
    def usedEndorsements(self, netid):

        query = "PREPARE stmt(text) AS " \
                "SELECT endorsements FROM students WHERE netid = $1;" \
                "EXECUTE stmt('" + netid + "');"

        endorsements = Database.connectDB(self, query)[0][0]

        return endorsements

    # ---------------------------------------------------------------------
    # returns 'flagged' or 'flag' depending on whether netid has
    # flagged speakid
    # ---------------------------------------------------------------------
    def hasFlagged(self, netid, speakid):

        query = "PREPARE stmt(text, text) AS " \
                "SELECT reason FROM reports WHERE netid = $1 AND speakid = $2;" \
                "EXECUTE stmt('" + netid + ", '" + str(speakid) + "');"

        reports = Database.connectDB(self, query)

        if reports and reports[0][0] != 0:
            return "Flagged"
        else:
            return "Flag"

    # ---------------------------------------------------------------------
    # returns a list of all of the reports that have been submitted
    # ---------------------------------------------------------------------
    def getReports(self):
        query = 'SELECT netid, speakid, reason FROM reports'
        result = Database.connectDB(self, query)

        reports = []
        for i in range(len(result)):
            reports.append(Report(result[i][0], result[i][1], result[i][2]))

        return reports

    # ---------------------------------------------------------------------
    # returns a list of all endorsed speakers with a name fitting
    # the search criteria
    # ---------------------------------------------------------------------
    def searchEndorsements(self, search, netid):
        search = search.lower()
        search = search.strip()
        search = '%' + search + '%'

        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM speakers WHERE LOWER(name) LIKE $1 AND NOT netid = $2;" \
                "EXECUTE stmt('" + search + "','" + netid.strip() + "');"

        speakers = Database.connectDB(self, query)

        speaker_list = []

        for i in range(len(speakers)):
            speaker_list.append(Speaker(speakers[i][0], speakers[i][1], speakers[i][2], speakers[i][3], speakers[i][4],
                                        speakers[i][5], speakers[i][6], speakers[i][7], speakers[i][8]))
        return speaker_list

    # ---------------------------------------------------------------------
    # Returns as a list all of the logs that fir the search criteria
    # ---------------------------------------------------------------------
    def searchAdminLogs(self, search):
        search = search.lower()

        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM adminlogs WHERE netid LIKE $1 ORDER BY date DESC;" \
                "EXECUTE stmt('%" + search + "%');"

        results = Database.connectDB(self, query)
        return results

    # ---------------------------------------------------------------------
    # returns a list of all the Speakers that have been nominated
    # ---------------------------------------------------------------------
    def getSpeakers(self):
        query = 'SELECT * FROM speakers'
        speakers = Database.connectDB(self, query)

        speaker_list = []

        for i in range(len(speakers)):
            speaker_list.append(Speaker(speakers[i][0], speakers[i][1], speakers[i][2], speakers[i][3], speakers[i][4],
                                        speakers[i][5], speakers[i][6], speakers[i][7], speakers[i][8]))
        return speaker_list

    # ---------------------------------------------------------------------
    # Returns the conversation information for the conversation with
    # converseid as Conversation object
    # ---------------------------------------------------------------------
    def getConversation(self, converseid):
        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM conversation WHERE converseid = $1;" \
                "EXECUTE stmt('" + str(converseid) + "');"

        conversation = Database.connectDB(self, query)

        if not conversation:
            conversation = 0
        else:
            conversation = conversation[0]
            conzip = json.loads(conversation[3])
            speakers = []
            descrips = []
            links = []
            images = []

            for converse in conzip.values():
                speakers.append(converse[0])
                descrips.append(converse[1])
                links.append(converse[2])
                images.append(converse[3])

            conversation = Conversation(conversation[0], conversation[1], conversation[2], speakers, descrips, links,
                                        images, conversation[4], conversation[5], conversation[6])

        return conversation

    # ---------------------------------------------------------------------
    def getConversations(self, promoted):
        if promoted == 0:
            query = "SELECT * FROM conversation WHERE faculty = '0'"
        else:
            query = "SELECT * FROM conversation WHERE faculty != '0'"
        conversations = Database.connectDB(self, query)

        conversation_list = []

        for i, conversation in enumerate(conversations):

            conzip = json.loads(conversation[3])
            speakers = []
            descrips = []
            links = []
            images = []

            for converse in conzip.values():
                speakers.append(converse[0])
                descrips.append(converse[1])
                links.append(converse[2])
                images.append(converse[3])

            conversation_list.append(
                Conversation(conversation[0], conversation[1], conversation[2], speakers, descrips, links, images,
                             conversation[4], conversation[5], conversation[6]))

        return conversation_list

    # ---------------------------------------------------------------------
    # returns a list of all the speakers that have reached the
    # threshold of endorsements
    # ---------------------------------------------------------------------
    def getEndorsed(self, threshold):

        query = "PREPARE stmt(int) AS " \
                "SELECT * FROM speakers WHERE endorsements >= $1;" \
                "EXECUTE stmt(" + str(threshold) + ");"

        result = Database.connectDB(self, query)
        endorsed_list = []
        for i in range(len(result)):
            if result[i][0] not in endorsed_list:
                endorsed_list.append(
                    Speaker(result[i][0], result[i][1], result[i][2], result[i][3], result[i][4], result[i][5],
                            result[i][6], result[i][7], result[i][8]))

        return endorsed_list

    # ---------------------------------------------------------------------
    # Returns as a list all of the conversations that have met the
    # of endorsements
    # ---------------------------------------------------------------------
    def getccEndorsed(self, threshold):

        query = "PREPARE stmt(int) AS " \
                "SELECT * FROM conversation WHERE endorsements >= $1;" \
                "EXECUTE stmt(" + str(threshold) + ");"

        conversations = Database.connectDB(self, query)

        conversation_list = []

        for i, conversation in enumerate(conversations):

            conzip = json.loads(conversation[3])
            speakers = []
            descrips = []
            links = []
            images = []

            for converse in conzip.values():
                speakers.append(converse[0])
                descrips.append(converse[1])
                links.append(converse[2])
                images.append(converse[3])

            conversation_list.append(
                Conversation(conversation[0], conversation[1], conversation[2], speakers, descrips, links, images,
                             conversation[4], conversation[5], conversation[6]))

        return conversation_list

    # ---------------------------------------------------------------------
    # allows the student with netid netid to endorse the speaker with
    # speakid speakid with count number of endorsements
    # ---------------------------------------------------------------------
    def endorse(self, netid, speakid, count):

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE students SET endorsements = endorsements + $1 WHERE netid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + netid.strip() + "');"

        Database.connectDB(self, query)

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE speakers SET endorsements = endorsements + $1 WHERE speakid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + str(speakid) + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows the student with netid netid to endorse the speaker with
    # speakid speakid with count number of endorsements
    # ---------------------------------------------------------------------
    def ccendorse(self, netid, converseid, count):

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE students SET ccendorsements = ccendorsements + $1 WHERE netid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + netid.strip() + "');"

        Database.connectDB(self, query)

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE conversation SET endorsements = endorsements + $1 WHERE converseid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + str(converseid) + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows the student with netid netid to endorse the speaker with
    # speakid speakid with count number of endorsements
    # ---------------------------------------------------------------------
    def fpromote(self, netid, converseid):

        query = "PREPARE stmt(text) AS " \
                "UPDATE conversation SET faculty = $1 WHERE converseid = $2;" \
                "EXECUTE stmt('" + netid.strip() + "', '" + str(converseid) + "');"

        Database.connectDB(self, query)

        query = "PREPARE stmt(text) AS " \
                "UPDATE faculty SET endorsements = 1 WHERE netid = $1;" \
                "EXECUTE stmt('" + netid.strip() + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows the student with netid netid to flag the speaker with
    # speakid speakid for reason reason
    # ---------------------------------------------------------------------
    def flag(self, netid, speakid, reason):

        query = "PREPARE stmt(text) AS " \
                "INSERT INTO reports VALUES($1, $2, $3);" \
                "EXECUTE stmt('" + netid.strip() + "', '" + str(speakid) + "', '" + prep(str(reason)) + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows admin to dismiss a flagged speaker
    # ---------------------------------------------------------------------
    def dismissFlag(self, speakid):

        query = "PREPARE stmt(text) AS " \
                "DELETE FROM reports WHERE speakid = $1;" \
                "EXECUTE stmt('" + str(speakid) + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Allows admin to delete the report
    # ---------------------------------------------------------------------
    def deleteReports(self):

        query = 'DELETE FROM reports'
        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Allows admin to remove the nomination
    # ---------------------------------------------------------------------
    def removeNomination(self, speakid):

        query = "PREPARE stmt(text) AS " \
                "DELETE FROM speakers WHERE speakid = $1;" \
                "EXECUTE stmt('" + str(speakid) + "');"
        Database.connectDB(self, query)

        query = "PREPARE stmt(text) AS " \
                "DELETE FROM reports WHERE speakid = $1;" \
                "EXECUTE stmt('" + str(speakid) + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows the student with netid netid to vote for the speaker
    # with speakid speakid
    # ---------------------------------------------------------------------
    def vote(self, netid, speakid, count):

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE speakers SET votes = votes + $1 WHERE speakid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + str(speakid) + "');"

        Database.connectDB(self, query)

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE students SET votes = votes + $1 WHERE netid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + netid.strip() + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Allows the student with netid to vote for the conversation with
    # converseid with count number of votes
    # ---------------------------------------------------------------------
    def ccvote(self, netid, converseid, count):

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE conversation SET votes = votes + $1 WHERE converseid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + str(converseid) + "');"

        Database.connectDB(self, query)

        query = "PREPARE stmt(int, text) AS " \
                "UPDATE students SET ccvotes = ccvotes + $1 WHERE netid = $2;" \
                "EXECUTE stmt(" + str(count) + ", '" + netid.strip() + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows access of an image for a particular speakid
    # ---------------------------------------------------------------------
    def getImage(self, speakid):

        query = "PREPARE stmt(text) AS " \
                "SELECT imglink FROM speakers WHERE speakid = $1;" \
                "EXECUTE stmt('" + str(speakid) + "');"

        imagelink = Database.connectDB(self, query)
        return imagelink

    # ---------------------------------------------------------------------
    # allows the student with netid netid to nominate a new speaker
    # by providing the speaker’s firstname, lastname, descrip.
    # Returns the speakid of the new speaker.
    # ---------------------------------------------------------------------
    def nominate(self, netid, cycle, name, descrip, links, imglink):
        query = 'SELECT ids FROM cycle'
        new_speakid = int(Database.connectDB(self, query)[0][0])
        query = "UPDATE cycle SET ids = ids + 1"
        Database.connectDB(self, query)

        query = "PREPARE stmt(text, text, text, text, text, text, text) AS " \
                "INSERT INTO speakers VALUES($1, $2, $3, $4, $5, $6, $7, 0, 0);" \
                "EXECUTE stmt('" + str(new_speakid) + "', '" + str(netid).strip() + "', '" + prep(
            str(cycle)) + "', '" + prep(str(name)) \
                + "', '" + prep(str(descrip)) + "', '" + prep(str(links)) + "', '" + prep(str(imglink)) + "');"

        Database.connectDB(self, query)

        query = "PREPARE stmt(text) AS " \
                "UPDATE students SET nominations = nominations + 1 WHERE netid = $1;" \
                "EXECUTE stmt('" + str(netid).strip() + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # allows the student with netid netid to nominate a new conversattion
    # by providing the appropriate information.
    # Returns the speakid of the new speaker.
    # ---------------------------------------------------------------------
    def ccnominate(self, netid, cycle, conzip):
        query = 'SELECT ccids FROM cycle'
        new_ccid = int(Database.connectDB(self, query)[0][0])
        query = "UPDATE cycle SET ccids = ccids + 1"
        Database.connectDB(self, query)

        query = "PREPARE stmt(text, text, text, text) AS " \
                "INSERT INTO conversation VALUES($1, $2, $3, $4, 0, 0, 0);" \
                "EXECUTE stmt('" + str(new_ccid) + "', '" + str(netid).strip() + "', '" + prep(
            str(cycle)) + "', '" + prep(str(conzip)) + "');"
        Database.connectDB(self, query)

        query = "PREPARE stmt(text) AS " \
                "UPDATE students SET ccnominations = ccnominations + 1 WHERE netid = $1;" \
                "EXECUTE stmt('" + str(netid).strip() + "');"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Creates a new cycle by specifying the appropriate information
    # ---------------------------------------------------------------------

    def createCycle(self, name, datecreated, admin, nominatenum, endorsenum, votenum, endorsethresh, rollthresh,
                    nomdate, endorsedate,
                    votingdate, resultsdate, enddate):
       
        query = 'SELECT MAX(speakid) FROM speakers'
        speakers = Database.connectDB(self, query)

        if not speakers or len(speakers) == 0:
            ids = 1
        else:
            ids = int(speakers[0][0]) + 1
            
        query = 'SELECT MAX(converseid) FROM conversation'
        converseids = Database.connectDB(self, query)
        print(converseids)
        if not converseids or len(converseids) == 0:
            ccids = 1
        else:
            ccids = int(converseids[0][0]) + 1
            
        query = 'DELETE FROM cycle'
        Database.connectDB(self, query)

        query = 'DELETE FROM students'
        Database.connectDB(self, query)

        query = 'DELETE FROM faculty'
        Database.connectDB(self, query)

        query = 'DELETE FROM reports'
        Database.connectDB(self, query)
        
        if not rollthresh:
            rollthresh = 0;
        query = "PREPARE stmt(text, date, text, int, int, int, int, int, int, date, date, date, date, date, int) AS " \
                "INSERT INTO cycle VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15);" \
                "EXECUTE stmt('" + prep(str(name)) + "', '" + prep(str(datecreated).strip()) + "', '" + prep(
            str(admin).strip()) + "', " + prep(str(ids)) \
                + ", " + prep(str(nominatenum)) + ", " + str(endorsenum) + ", " + str(votenum) + ", " + str(
            endorsethresh) \
                + ", " + str(rollthresh) + ", '" + str(nomdate) + "', '" + str(endorsedate) + "', '" + str(
            votingdate) + "', '" + \
                str(resultsdate) + "', '" + str(enddate) + "', " + str(ccids) + ");"

        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Adjusts the database
    # ---------------------------------------------------------------------
    def adjustDatabase(self, rolloverNom, rolloverEnd, rolloverVot, rolloverThresh):
        if rolloverNom:
            if rolloverEnd:
                if rolloverThresh:
                    query = "PREPARE stmt(int) AS " \
                            "UPDATE speakers SET endorsements = 0 WHERE endorsements < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"

                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "UPDATE conversation SET endorsements = 0 WHERE endorsements < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"

                    Database.connectDB(self, query)
            else:
                query = 'UPDATE speakers SET endorsements = 0'
                Database.connectDB(self, query)

                query = 'UPDATE conversation SET endorsements = 0'
                Database.connectDB(self, query)
            if rolloverVot:
                if rolloverThresh:
                    query = "PREPARE stmt(int) AS " \
                            "UPDATE speakers SET votes = 0 WHERE votes < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"

                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "UPDATE conversation SET votes = 0 WHERE votes < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"

                    Database.connectDB(self, query)
            else:
                query = 'UPDATE speakers SET votes = 0'
                Database.connectDB(self, query)

                query = 'UPDATE conversation SET votes = 0'
                Database.connectDB(self, query)

        elif rolloverEnd:
            if rolloverVot:
                if rolloverThresh:
                    query = "PREPARE stmt(int, int) AS " \
                            "DELETE FROM speakers WHERE endorsements < $1 AND votes < $2;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ", " + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "UPDATE speakers SET endorsements = 0 WHERE endorsements < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "UPDATE speakers SET votes = 0 WHERE votes < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int, int) AS " \
                            "DELETE FROM conversation WHERE endorsements < $1 AND votes < $2;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ", " + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "UPDATE conversation SET endorsements = 0 WHERE endorsements < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "UPDATE conversation SET votes = 0 WHERE votes < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

            else:
                if rolloverThresh:
                    query = "PREPARE stmt(int) AS " \
                            "DELETE FROM speakers WHERE endorsements < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                    query = "PREPARE stmt(int) AS " \
                            "DELETE FROM conversation WHERE endorsements < $1;" \
                            "EXECUTE stmt(" + str(rolloverThresh) + ");"
                    Database.connectDB(self, query)

                query = 'UPDATE speakers SET votes = 0'
                Database.connectDB(self, query)

                query = 'UPDATE conversation SET votes = 0'
                Database.connectDB(self, query)

        elif rolloverVot:
            if rolloverThresh:
                query = "PREPARE stmt(int) AS " \
                        "DELETE FROM speakers WHERE votes < $1;" \
                        "EXECUTE stmt(" + str(rolloverThresh) + ");"
                Database.connectDB(self, query)

                query = "PREPARE stmt(int) AS " \
                        "DELETE FROM conversation WHERE votes < $1;" \
                        "EXECUTE stmt(" + str(rolloverThresh) + ");"
                Database.connectDB(self, query)

            query = 'UPDATE speakers SET endorsements = 0'
            Database.connectDB(self, query)

            query = 'UPDATE conversation SET endorsements = 0'
            Database.connectDB(self, query)

        else:
            query = 'DELETE FROM speakers'
            Database.connectDB(self, query)

            query = 'DELETE FROM conversation'
            Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Authenticates an admin
    # ---------------------------------------------------------------------
    def adminAuthenticate(self, username):
        query = "PREPARE stmt(text) AS " \
                "SELECT * FROM admin WHERE netid = $1;" \
                "EXECUTE stmt('" + username.strip() + "');"
        exists = Database.connectDB(self, query)
        return len(exists)

    # ---------------------------------------------------------------------
    # Adds an admin
    # ---------------------------------------------------------------------
    def addAdmin(self, newAdmin):
        query = "PREPARE stmt(text) AS " \
                "INSERT INTO admin VALUES($1);" \
                "EXECUTE stmt('" + newAdmin.strip() + "');"
        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # Removes an admin
    # ---------------------------------------------------------------------
    def removeAdmin(self, oldAdmin):
        query = "PREPARE stmt(text) AS " \
                "DELETE FROM admin WHERE netid = $1;" \
                "EXECUTE stmt('" + oldAdmin.strip() + "');"
        Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # returns the count of a table
    # ---------------------------------------------------------------------
    def returnCount(self, table):
        query = "PREPARE stmt(text) AS " \
                "SELECT COUNT(*) FROM $1; " \
                "EXECUTE stmt('" + table.strip() + "');"
        return Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # returns the list of admins
    # ---------------------------------------------------------------------
    def returnAdmins(self):
        query = 'SELECT * FROM admin'
        return Database.connectDB(self, query)

    # ---------------------------------------------------------------------
    # returns the list of logs
    # ---------------------------------------------------------------------
    def returnAdminLogs(self):
        query = 'SELECT * FROM adminlogs ORDER BY date DESC'
        info = Database.connectDB(self, query)
        return info

    # ---------------------------------------------------------------------
    # Creates a new log
    # ---------------------------------------------------------------------
    def addLog(self, date, netid, action, info):
        query = "PREPARE stmt(timestamp, text, int, text) AS " \
                "INSERT INTO adminlogs VALUES($1, $2, $3, $4);" \
                "EXECUTE stmt('" + str(date) + "', '" + netid.strip() + "', " + str(
            action) + ", '" + info.strip() + "');"
        Database.connectDB(self, query)


# ---------------------------------------------------------------------
if __name__ == '__main__':
    database = Database()
