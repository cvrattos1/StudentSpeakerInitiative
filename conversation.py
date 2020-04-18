class Conversation:
    def __init__(self,  converseid, netid, cycle, names, descrips, links, imglinks, endorsements, votes, faculty):
        self._converseid = converseid
        self._netid = netid
        self._cycle = cycle
        self._names = names
        self._descrips = descrips
        self._links = links
        self._imglinks = imglinks
        self._endorsements = endorsements
        self._votes = votes
        self._faculty = faculty

    def getConverseId(self):
        return self._converseid

    def getNetid(self):
        return self._netid

    def getCycle(self):
        return self._cycle

    def getNames(self):
        return self._names

    def getDescrips(self):
        return self._descrips

    def getLinks(self):
        return self._links

    def getImgLinks(self):
        print(self._imglink)
        return self._imglinks

    def getEndorsements(self):
        return self._endorsements

    def getVotes(self):
        return self._votes
    
    def getFaculty(self):
        return self._faculty


    def getSpeakers(self):
        spkrCount = len(self._names)
        spkrList=[]
        for i in range(spkrCount):
            spkr=[self._names[i], self._descrips[i], self._links[i], self._imglinks[i]]
            spkrList.append(spkr)
        return spkrList 
