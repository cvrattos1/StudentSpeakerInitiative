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

        return speaker_list


    # returns a list of all the speakids of speakers that have reached the threshold threshold of endorsements
    def getEndorsed(self, threshold):
        query = 'SELECT speakid FROM endorsements WHERE count >= ' + str(threshold)
        endorsed = Database.connectDB(self, query)

        endorsed_list = []
        for i in range(len(endorsed)):
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

    # allows the student with netid netid to endorse the speaker with speakid speakid with count number of endorsements
    def endorse(self, s_netid, s_speakid, s_count):
        query = 'SELECT count FROM endorsements WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
        exists = Database.connectDB(self, query)
        if len(exists) == 0:
            query = 'INSERT INTO endorsements VALUES (' + '\'' + s_netid + '\', \'' + s_speakid + '\', \'' + str(s_count) + '\')'
            Database.connectDB(self, query)
        else:
            query = 'UPDATE endorsements SET count = ' + str(s_count) + ' WHERE netid = \'' + s_netid + '\' AND speakid = \'' + s_speakid + '\''
            Database.connectDB(self, query)

    # allows the student with netid netid to vote for the speaker with speakid speakid
    def vote(self, s_netid, s_speakid):
        query = 'UPDATE speakers SET votes = votes + 1 WHERE speakid = ' + '\'' + s_speakid + '\''
        Database.connectDB(self, query)

        query = 'INSERT INTO votes VALUES (' + '\'' + s_netid + '\', 1)'
        Database.connectDB(self, query)

    # allows the student with netid netid to nominate a new speaker by providing the speaker’s firstname, lastname, descrip. Returns the speakid of the new speaker.
    def nominate(self, s_netid, s_firstname, s_lastname, s_descrip):
        query = 'SELECT * FROM speakers'
        speakers = Database.connectDB(self, query)
        new_speakid = str(len(speakers))

        query = 'INSERT INTO speakers VALUES (' + '\'' + new_speakid + '\', \'' + s_firstname + '\', \'' + s_lastname + \
                '\', \'' + s_descrip + '\', 0)'
        Database.connectDB(self, query)

        query = 'INSERT INTO nominations VALUES (' + '\'' + s_netid + '\', \'' + new_speakid + '\')'
        Database.connectDB(self, query)



# ---------------------------------------------------------------------

