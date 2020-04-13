#!usr/bin/env python

# ---------------------------------------------------------------------
# database.py
# Author: Caroline di Vittorio
# ---------------------------------------------------------------------

import os
import psycopg2

from student import Student
from speaker import Speaker
from cycle import Cycle
from report import Report
from conversation import Conversation

UNLIMITED_VALUE = 2147483647

class Database:

    # connect to the database and execute query, return result of query, if there is one.
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
            return []

    # ---------------------------------------------------------------------

    # returns the information about the student with netid as a Student object, or None if does not exist
    def getStudent(self, netid):
        query = "SELECT * from students WHERE netid = '" + netid.strip() + "'"
        print(query)
        result = Database.connectDB(self, query)

        if not result:
            return None
        student = Student(netid, result[0][1], result[0][2], result[0][3])
        return student
    
    def makeStudent(self, netid):
        query = "INSERT INTO students VALUES('" + netid.strip() + "', 0, 0, 0)"
        print(query)
        result = Database.connectDB(self, query)

    # ---------------------------------------------------------------------

    # returns the information about the speaker with speakid as a Speaker object, or None if does not exist
    def getSpeaker(self, speakid):
        query = "SELECT * from speakers WHERE speakid = '" + speakid + "'"
        result = Database.connectDB(self, query)

        if not result:
            return None
        speaker = Speaker(speakid, result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6], result[0][7], result[0][8])
        return speaker

    # ---------------------------------------------------------------------

    def getCycle(self):
        query = "SELECT * from cycle"
        result = Database.connectDB(self, query)

        if not result:
            return None
        else:
            return Cycle(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5],
                         result[0][6], result[0][7], result[0][8], result[0][9],result[0][10],result[0][11])

    # ---------------------------------------------------------------------

    # returns as an integer the number of endorsements remaining for the student with netid netid
    def hasEndorsed(self, netid):
        query = "SELECT endorsements FROM students WHERE netid = '" + netid + "'"
        endorsements = Database.connectDB(self, query)
        if not endorsements:
            return 0
        else:
            return endorsements

    # ---------------------------------------------------------------------

    # returns as an integer the number of endorsements remaining for the student with netid netid
    def remainingNominations(self, netid):
        query = "SELECT nominations FROM students WHERE netid = '" + netid.strip() + "'"
        print(query)
        noms = Database.connectDB(self, query)
        if noms:
            nominations=noms[0][0]
        else:
            nominations=0

        query = "SELECT nominatenum FROM cycle"
        allowance = Database.connectDB(self, query)[0][0]

        if allowance == UNLIMITED_VALUE:
            return "unlmited"
        else:
            return allowance - nominations
        
    def remainingccNominations(self, netid):
        query = "SELECT ccnominations FROM students WHERE netid = '" + netid.strip() + "'"
        ccnoms = Database.connectDB(self, query)
        if ccnoms:
            ccnominations=ccnoms[0][0]
        else:
            ccnominations=0

        query = "SELECT nominatenum FROM cycle"
        allowance = Database.connectDB(self, query)[0][0]

        if allowance == UNLIMITED_VALUE:
            return "unlmited"
        else:
            return allowance - ccnominations


    # ---------------------------------------------------------------------

    # returns as an integer the number of endorsements remaining for the student with netid netid
    def hasVoted(self, netid):
        query = "SELECT votes FROM students WHERE netid = '" + netid + "'"
        votes = Database.connectDB(self, query)
        if not votes:
            return 0
        else:
            return votes

    # ---------------------------------------------------------------------

    # returns as an integer the number of endorsements that the student with netid netid has currently used
    def usedEndorsements(self, netid):
        query = "SELECT endorsements FROM students WHERE netid = '" + netid + "'"
        endorsements = Database.connectDB(self, query)[0][0]

        return endorsements

    # ---------------------------------------------------------------------

    # returns 'flagged' or 'flag' depending on whether netid has flagged speakid
    def hasFlagged(self, netid, speakid):
        query = 'SELECT reason FROM reports WHERE netid = ' + '\'' + netid + '\' AND speakid = \'' + speakid + '\''
        reports = Database.connectDB(self, query)

        if reports and reports[0][0] != 0:
            return "Flagged"
        else:
            return "Flag"

    # ---------------------------------------------------------------------

    # returns a list of all of the reports that have been submitted
    def getReports(self):
        query = 'SELECT netid, speakid, reason FROM reports'
        result = Database.connectDB(self, query)

        reports = []
        for i in range(len(result)):
            reports.append(Report(result[i][0], result[i][1], result[i][2]))

        return reports

    # ---------------------------------------------------------------------

    # returns a list of all the Speakers that have been nominated
    def getSpeakers(self):
        query = 'SELECT * FROM speakers'
        speakers = Database.connectDB(self, query)

        speaker_list = []

        for i in range(len(speakers)):
            speaker_list.append(Speaker(speakers[i][0], speakers[i][1], speakers[i][2], speakers[i][3], speakers[i][4],
                                        speakers[i][5], speakers[i][6], speakers[i][7], speakers[i][8]))
        return speaker_list

    # ---------------------------------------------------------------------

    # returns a list of all the speakers that have reached the threshold threshold of endorsements
    def getEndorsed(self, threshold):
        query = 'SELECT * FROM speakers WHERE endorsements >= ' + str(threshold)
        result = Database.connectDB(self, query)
        endorsed_list = []
        for i in range(len(result)):
            if result[i][0] not in endorsed_list:
                endorsed_list.append(Speaker(result[i][0], result[i][1], result[i][2], result[i][3], result[i][4], result[i][5], result[i][6], result[i][7], result[i][8]))

        return endorsed_list

    # ---------------------------------------------------------------------

    # allows the student with netid netid to endorse the speaker with speakid speakid with count number of endorsements
    def endorse(self, netid, speakid, count):
        query = "UPDATE students SET endorsements = endorsements + " + str(count) + " WHERE netid = '" + netid.strip() + "'"
        print(query)
        Database.connectDB(self, query)

        query = "UPDATE speakers SET endorsements = endorsements + " + str(count) + " WHERE speakid = '" + speakid + "'"
        Database.connectDB(self, query)

    # allows the student with netid netid to flag the speaker with speakid speakid for reason reason
    def flag(self, netid, speakid, reason):
        query = "INSERT INTO reports VALUES('" + netid + "', '" + speakid + "', '" + "', '" + reason + "')"
        Database.connectDB(self, query)


    # allows admin to dismiss a flagged speaker
    def dismissFlag(self, netid, speakid):
        query = 'SELECT speakid FROM reports WHERE netid = \'' + netid + '\' AND speakid = \'' + speakid + '\''
        exists = Database.connectDB(self, query)
        if len(exists) == 1:
            query = 'DELETE FROM reports WHERE netid = \'' + netid + '\' AND speakid = \'' + speakid + '\''
            Database.connectDB(self, query)

    def removeNomination(self, speakid):
        query = "DELETE FROM speakers WHERE speakid = '" + speakid + "'"
        Database.connectDB(self, query)


    # allows the student with netid netid to vote for the speaker with speakid speakid
    def vote(self, netid, speakid):
        query = 'UPDATE speakers SET votes = votes + 1 WHERE speakid = ' + '\'' + speakid + '\''
        Database.connectDB(self, query)

        query = 'UPDATE students SET votes = votes + 1 WHERE netid = ' + '\'' + netid.strip() + '\''
        Database.connectDB(self, query)

    # allows access of an image for a particular speakid
    def getImage(self, speakid):
        query = 'SELECT imglink FROM speakers WHERE speakid = ' + '\'' + speakid + '\''
        imagelink = Database.connectDB(self, query)
        return imagelink

    # allows the student with netid netid to nominate a new speaker by providing the speaker’s firstname, lastname, descrip. Returns the speakid of the new speaker.
    def nominate(self, netid, cycle, name, descrip, links, imglink):
        query = 'SELECT ids FROM cycle'
        new_speakid = int(Database.connectDB(self, query)[0][0])
        print(new_speakid)
        query = "UPDATE cycle SET ids = ids + 1"
        Database.connectDB(self, query)

        query = 'INSERT INTO speakers VALUES (\'' + str(new_speakid) + '\', \'' + str(netid).strip() + '\', \'' + str(cycle) + '\', \'' \
                + str(name) + '\', \'' + str(descrip) + '\', \'' + str(links) + '\', \'' + str(imglink) + '\', 0, 0)'
        print(query)
        Database.connectDB(self, query)
        
        query = 'UPDATE students SET nominations = nominations + 1 WHERE netid = \'' + str(netid).strip() + '\''
        print(query)
        Database.connectDB(self, query)
        
    def ccnominate(self, netid, cycle, names, descrips, links, imglinks):
        query = 'SELECT ccids FROM cycle'
        new_ccid = int(Database.connectDB(self, query)[0][0])
        query = "UPDATE cycle SET ccids = ccids + 1"
        Database.connectDB(self, query)

        query = 'INSERT INTO conversation VALUES (\'' + str(new_ccid) + '\', \'' + str(netid).strip() + '\', \'' + str(cycle) + '\', \'' \
                + str(names) + '\', \'' + str(descrips) + '\', \'' + str(links) + '\', \'' + str(imglinks) + '\', 0, 0, 0)'
        print (query)        
        Database.connectDB(self, query)
        
        query = 'UPDATE students SET ccnominations = ccnominations + 1 WHERE netid = \'' + str(netid).strip() + '\''
        
        Database.connectDB(self, query)

    def createCycle(self, name, datecreated, admin, nominatenum, endorsenum, votenum, threshold, nomdate, endorsedate, datevoting, dateend):
        query = 'SELECT ids FROM cycle'
        result = Database.connectDB(self, query)
        if not result:
            ids = 0
        else:
            ids = int(result[0][0])
            
        query = 'SELECT ccids FROM cycle'
        result = Database.connectDB(self, query)
        if not result:
            ccids = 0
        else:
            ccids = int(result[0][0])

        query='DELETE FROM cycle'
        Database.connectDB(self, query)

        query = 'INSERT INTO cycle VALUES (\'' + str(name) + '\', \'' + str(datecreated) + '\', \'' + str(admin) + \
                '\', \'' + str(ids) + '\', \'' + str(nominatenum) + '\', \'' + str(endorsenum) + '\', \'' + \
                str(votenum) + '\', \'' + str(threshold) + '\', \'' + str(nomdate) + '\', \'' + str(endorsedate) + '\', \'' + str(datevoting) + '\', \'' +  str(dateend) + '\', \''+ str(ccids) + '\')'
        print (query)
        Database.connectDB(self, query)

    def adminAuthenticate(self, username):
        query = 'SELECT  * FROM admin WHERE netid = ' + '\'' + username.strip() + '\''
        exists = Database.connectDB(self, query)
        return len(exists)

        # returns nothing

    def addAdmin(self, newAdmin):
        query = 'INSERT INTO admin VALUES (' + '\'' + newAdmin.strip() + '\')'
        Database.connectDB(self, query)

    def removeAdmin(self, oldAdmin):
        query = 'DELETE FROM admin WHERE netid = ' + '\'' + oldAdmin.strip() + '\''
        Database.connectDB(self, query)

    def returnCount(self, table):
        query = 'SELECT COUNT(*) FROM ' + '\'' + table.strip() + '\''
        return Database.connectDB(self, query)



# ---------------------------------------------------------------------
if __name__ == '__main__':
    database = Database()
