class Student:
    def __init__(self,  netid, nominations, endorsements, votes):
        self._netid = netid
        self._nominations = nominations
        self._endorsements = endorsements
        self._votes = votes

    def getNetid(self):
        return self._netid

    def getNominations(self):
        return self._nominations

    def getEndorsements(self):
        return self._endorsements

    def getVotes(self):
        return self._votes

    def printStudent(self):
        print(str(self._netid) + " " + str(self._nominations) + " " + str(self._endorsements) + " " + str(self._votes))