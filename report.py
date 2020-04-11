class Report:
    def __init__(self,  netid, speakid, reason):
        self._netid = netid
        self._speakid = speakid
        self._reason = reason


    def getNetid(self):
        return self._netid

    def getSpeakid(self):
        return self._speakid

    def getReason(self):
        return self._reason

