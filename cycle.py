class Cycle:
    def __init__(self,  name, datecreated, admin, ids, nominatenum, endorsenum, votenum, threshold, datevoting, dateend):
        self._name = name
        self._datecreated = datecreated
        self._admin = admin
        self._ids = ids
        self._nominatenum = nominatenum
        self._endorsenum = endorsenum
        self._votenum = votenum
        self._threshold = threshold
        self._datevoting = datevoting
        self._dateend = dateend

    def getName(self):
        return self._name

    def getDateCreated(self):
        return self._datecreated

    def getAdmin(self):
        return self._admin

    def getIds(self):
        return self._ids

    def getNominateNum(self):
        return self._nominatenum

    def getEndorseNum(self):
        return self._endorsenum

    def getVoteNum(self):
        return self._votenum

    def getThreshold(self):
        return self._threshold

    def getDateVoting(self):
        return self._datevoting

    def getDateEnd(self):
        return self._dateend
