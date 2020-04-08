import ldap3

class ServerConnection:
    def __init__(self, username, password):
        self.username = username  
        self.password = password


def __serversearch(serverconnection, uid ,att):
    username = serverconnection.username;
    password = serverconnection.password;
    server = ldap3.Server('ldap.princeton.edu', 636, use_ssl=True)
    connect = ldap3.Connection(server, "uid=" + username + ",o=princeton university,c=us", password)
    connect.bind()
    result = connect.search("o=princeton university,c=us","(&(uid=" + uid + ")(pustatus=" + att + "))")
    return result

def isFaculty(serverconnection, uid):
    return __serversearch(serverconnection, uid, "fac")
    
def isUndergraduate(serverconnection, uid):
    return __serversearch(serverconnection, uid, "u*")
    
def isGraduateStudent(serverconnection, uid):
    return __serversearch(serverconnection, uid, "g*")
