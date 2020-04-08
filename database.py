#!usr/bin/env python

# ---------------------------------------------------------------------
# database.py
# Author: Caroline di Vittorio
# ---------------------------------------------------------------------

import os
import psycopg2

# ---------------------------------------------------------------------
TOTAL_ENDORSEMENTS = 10
# ---------------------------------------------------------------------

class Database:

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

    # returns 1 if the student with netid netid has voted, and 0 otherwise
    def hasVoted(self, s_netid):
        query = 'SELECT voted FROM votes WHERE netid = ' + '\'' + s_netid + '\''
        voted = Database.connectDB(self, query)

        if len(voted) == 0:
            return 0
        else:
            return voted[0][0]


    # returns 1 if the student with netid netid has nominated a speaker, and 0 otherwise
    def hasNominated(self, s_netid):
        query = 'SELECT speakid FROM nominations WHERE netid = ' + '\'' + s_netid + '\''
        nominated = Database.connectDB(self, query)

        if len(nominated) == 0:
            return 0
        else:
            return 1


    # returns as an integer the number of endorsements remaining for the student with netid netid
    def remainingEndorsements(self, s_netid):
        query = 'SELECT count FROM endorsements WHERE netid = ' + '\'' + s_netid + '\''
        endorsements = Database.connectDB(self, query)

        if len(endorsements) == 0:
            return TOTAL_ENDORSEMENTS
        else:
            remaining = TOTAL_ENDORSEMENTS
            for i in range(len(endorsements)):
                remaining = remaining - endorsements[i][0]
            return remaining


    # returns as an integer the number of endorsements that the student with netid netid has currently used
    def usedEndorsements(self, s_netid):
        query = 'SELECT count FROM endorsements WHERE netid = ' + '\'' + s_netid + '\''
        endorsements = Database.connectDB(self, query)

        if len(endorsements) == 0:
            return 0
        else:
            total = 0
            for i in range(len(endorsements)):
                total = total + endorsements[i][0]
            return total


    # returns a list of tuples: each tuple contains the speakid of the speaker that the student with netid netid has
    # endorsed, as well as the number of endorsements that the student has used on that speaker
    def getEndorsements(self, s_netid):
        query = 'SELECT speakid, count FROM endorsements WHERE netid = ' + '\'' + s_netid + '\''
        endorsements = Database.connectDB(self, query)
        return endorsements
    
    # returns the string Endorse or Unendorse depending on if the student with netid has endorsed the speaker with
    # speakid or not
    def hasEndorsed(self, s_netid, s_speakid):
        query = 'SELECT speakid, count FROM endorsements WHERE netid = ' + '\'' + s_netid + '\''
        endorsements = Database.connectDB(self, query)
        idlist = []
        for ids, _ in endorsements:
            idlist.append(ids)
        if s_speakid in idlist:
            return "Unendorse"
        else:
            return "Endorse"

    # returns True or False depending on if the student with netid s_netid has flagged the speakid
    # s_speakid or not
    def hasFlagged(self, s_netid, s_speakid):
        query = 'SELECT speakid FROM reports WHERE netid = ' + '\'' + s_netid + '\''
        reports = Database.connectDB(self, query)

        idlist = []
        for report in reports:
            idlist.append(report[0])
        if s_speakid in idlist:
            return "Flagged"
        else:
            return "Flag"

    # returns a list of all of the reports that have been submitted
    def getReports(self):
        query = 'SELECT netid, speakid, reason FROM reports'
        reports = Database.connectDB(self, query)
        return reports

    # returns the speakid of the speaker that the student with netid netid has nominated if it exists, None otherwise
    def getNomination(self, s_netid):
        query = 'SELECT speakid FROM nominations WHERE netid = ' + '\'' + s_netid + '\''
        nomination = Database.connectDB(self, query)

        if len(nomination) == 0:
            return None
        else:
            return nomination[0][0]


    # returns a list of all the speakids of speakers that have been nominated, empty list if no speakers
    def getSpeakers(self):
        query = 'SELECT speakid FROM speakers'
        speakers = Database.connectDB(self, query)

        speaker_list = []
        for i in range (len(speakers)):
            speaker_list.append(speakers[i][0])
        print(speaker_list)
        return speaker_list


    # returns a list of all the speakids of speakers that have reached the threshold threshold of endorsements
    def getEndorsed(self, threshold):
        query = 'SELECT speakid FROM endorsements WHERE count >= ' + str(threshold)
        endorsed = Database.connectDB(self, query)
        endorsed_list = []
        for i in range(len(endorsed)):
            if endorsed[i][0] not in endorsed_list:
                endorsed_list.append(endorsed[i][0])
        
        return endorsed_list


    # returns the first name of the speaker with speakid speakid, None if speaker does not exist
    def getSpeakerFirstName(self, s_speakid):
        query = 'SELECT firstname FROM speakers WHERE speakid = ' + '\'' + s_speakid + '\''
        firstname = Database.connectDB(self, query)
        if len(firstname) == 0:
            return None
        else:
            return firstname[0][0]

    # returns the last name of the speaker with speakid speakid
    def getSpeakerLastName(self, s_speakid):
        query = 'SELECT lastname FROM speakers WHERE speakid = ' + '\'' + s_speakid + '\''
        lastname = Database.connectDB(self, query)
        if len(lastname) == 0:
            return None
        else:
            return lastname[0][0]

    # returns the description of the speaker with speakid speakid
    def getSpeakerDescription(self, s_speakid):
        query = 'SELECT descrip FROM speakers WHERE speakid = ' + '\'' + s_speakid + '\''
        descrip = Database.connectDB(self, query)
        if len(descrip) == 0:
            return None
        else:
            return descrip[0][0]

    # returns the number of votes given to the speaker with speakid speakid, None if speaker does not exist
    def getSpeakerVotes(self, s_speakid):
        query = 'SELECT votes FROM speakers WHERE speakid = ' + '\'' + s_speakid + '\''
        votes = Database.connectDB(self, query)
        if len(votes) == 0:
            return None
        else:
            return votes[0][0]

    # returns the number of endorsements given to the speaker with speakid speakid, None if speaker does not exits
    def getSpeakerEndorsements(self, s_speakid):
        query = 'SELECT count FROM endorsements  WHERE speakid = ' + '\'' + s_speakid + '\''
        endorsements = Database.connectDB(self, query)
        if len(endorsements) == 0:
            return None
        else:
            total = 0;
            for i in range(len(endorsements)):
                total = total + endorsements[i][0]
            return total
    
    def adminClearTables(self):
        query = "SELECT table_schema, table_name FROM information_schema.tables WHERE ( table_schema = 'public' ) ORDER BY table_schema, table_name;"
        tables = Database.connectDB(self, query) 
        tables.remove(('public', 'cycleinfo'))
        tablelist = []
        for _, table in tables:
            Database.connectDB(self, "DELETE FROM " + table + ";")
        
    def votePeriod(self):
        query = 'SELECT votingperiod FROM cycleinfo'
        votingperiod = Database.connectDB(self, query) 
        return votingperiod[0][0]
    
    def changePeriod(self,currentPeriod):
        query = 'UPDATE cycleinfo SET votingperiod = ' + str(currentPeriod)
        Database.connectDB(self, query)
        
    # allows the student with netid netid to endorse the speaker with speakid speakid with count number of endorsements
    def endorse(self, s_netid, s_speakid, s_count):
        query = 'SELECT count FROM endorsements WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
        exists = Database.connectDB(self, query)
        if len(exists) == 0:
            query = 'INSERT INTO endorsements VALUES (' + '\'' + s_netid + '\', \'' + s_speakid + '\', \'' + str(s_count) + '\')'
            Database.connectDB(self, query)

    # allows the student with netid netid to flag the speaker with speakid speakid for reason reason
    def flag(self, s_netid, s_speakid, reason):
        query = 'SELECT speakid FROM reports WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
        exists = Database.connectDB(self, query)
        print('called')
        if len(exists) == 0:
            print('inserted')
            query = 'INSERT INTO reports VALUES (' + '\'' + s_netid + '\', \'' + s_speakid + '\', \'' + str(reason) + '\')'
            Database.connectDB(self, query)
            
    # allows the student with netid netid to unendorse the speaker with speakid speakid with count number of endorsements        
    def unendorse(self, s_netid, s_speakid, s_count):
        query = 'SELECT count FROM endorsements WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
        exists = Database.connectDB(self, query)
        print(len(exists))
        if len(exists) == 1:
            print("yes")
            query = 'DELETE FROM endorsements WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
            Database.connectDB(self, query)

    # allows admin to dismiss a flagged speaker
    def dismissFlag(self, s_netid, s_speakid):
        query = 'SELECT speakid FROM reports WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
        exists = Database.connectDB(self, query)
        if len(exists) == 1:
            query = 'DELETE FROM reports WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
            Database.connectDB(self, query)

    def removeNomination(self, s_speakid):
        query = 'SELECT netid FROM endorsements WHERE speakid = \'' + s_speakid + '\''
        query = 'SELECT FROM endorsements WHERE netid IN (' + query + ')'
        endorsements = Database.connectDB(self, query)
        print(endorsements)
        # query = 'DELETE FROM speakers WHERE speakid = \'' + s_speakid +'\''
        # Database.connectDB(self, query)
        # query = 'DELETE FROM reports WHERE speakid = \'' + s_speakid +'\''
        # Database.connectDB(self, query)

    # allows the student with netid netid to vote for the speaker with speakid speakid
    def vote(self, s_netid, s_speakid):
        query = 'UPDATE speakers SET votes = votes + 1 WHERE speakid = ' + '\'' + s_speakid + '\''
        Database.connectDB(self, query)

        query = 'INSERT INTO votes VALUES (' + '\'' + s_netid + '\', 1)'
        Database.connectDB(self, query)

    # allows access of an image for a particular speakid
    def getImage(self, s_speakid):
        query = 'SELECT imagelink FROM speakers WHERE speakid = ' + '\'' + s_speakid + '\''
        imagelink = Database.connectDB(self, query)
        return imagelink

    # allows the student with netid netid to nominate a new speaker by providing the speaker’s firstname, lastname, descrip. Returns the speakid of the new speaker.
    def nominate(self, s_netid, s_firstname, s_lastname, s_descrip, s_imglink):
        query = 'SELECT * FROM speakers'
        speakers = Database.connectDB(self, query)
        new_speakid = str(len(speakers))

        print(s_descrip)

        query = 'INSERT INTO speakers VALUES (' + '\'' + new_speakid + '\', \'' + s_firstname + '\', \'' + s_lastname + \
                '\', \'' + s_descrip + '\', \'' + s_imglink + '\', 0)'
        Database.connectDB(self, query)

        query = 'INSERT INTO nominations VALUES (' + '\'' + s_netid + '\', \'' + new_speakid + '\')'
        Database.connectDB(self, query)



# ---------------------------------------------------------------------

