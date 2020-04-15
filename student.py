class Student:
    def __init__(self,  netid, nominations, endorsements, votes, ccnominations, ccendorsements, ccvotes):
        self._netid = netid
        self._nominations = nominations
        self._endorsements = endorsements
        self._votes = votes
        self._ccnominations = ccnominations
        self._ccendorsements = ccendorsements
        self._ccvotes = ccvotes

    def getNetid(self):
        return self._netid

    def getNominations(self):
        return self._nominations

    def getEndorsements(self):
        return self._endorsements

    def getVotes(self):
        return self._votes
    
    def getccNominations(self):
        return self._ccnominations

    def getccEndorsements(self):
        return self._ccendorsements

    def getccVotes(self):
        return self._ccvotes

    def printStudent(self):
        print(str(self._netid) + " " + str(self._nominations) + " " + str(self._endorsements) + " " + str(self._votes))