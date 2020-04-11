class Conversation:
    def __init__(self,  converseid, netid, faculty, speakers, endorsements, votes):
        self._converseid = converseid
        self._netid = netid
        self._faculty = faculty
        self._speakers = speakers
        self._endorsements = endorsements
        self._votes = votes

    def getConverseid(self):
        return self._converseid

    def getNetid(self):
        return self._netid

    def getFaculty(self):
        return self._faculty

    def getSpeakers(self):
        return self._speakers

    def getEndorsements(self):
        return self._endorsements

    def getVotes(self):
        return self._votes