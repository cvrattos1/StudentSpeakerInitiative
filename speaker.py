class Speaker:
    def __init__(self,  speakid, netid, cycle, name, descrip, links, imglink, endorsements, votes):
        self._speakid = speakid
        self._netid = netid
        self._cycle = cycle
        self._name = name
        self._descrip = descrip
        self._links = links
        self._imglink = imglink
        self._endorsements = endorsements
        self._votes = votes

    def getSpeakid(self):
        return self._speakid

    def getNetid(self):
        return self._netid

    def getCycle(self):
        return self._cycle

    def getName(self):
        return self._name

    def getDescrip(self):
        return self._descrip

    def getLinks(self):
        return self._links

    def getImgLink(self):
        print(self._imglink)
        return self._imglink

    def getEndorsements(self):
        return self._endorsements

    def getVotes(self):
        return self._votes
