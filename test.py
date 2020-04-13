import ldap3

server = ldap3.Server('ldap.princeton.edu', 636, use_ssl=True)
connect = ldap3.Connection(server, "uid=thomascj,o=princeton university,c=us", "Poiuy123!@#")
connect.bind()
#result = connect.search("o=princeton university,c=us","(&(uid=thomascj)(pustatus=fac))")
result = connect.search("o=princeton university,c=us","(pustatus=fac)", attributes="uid")
print(result)
#import ldap3
#
#server = ldap3.Server('ldap.princeton.edu', port= 389)
#connect = ldap3.Connection(server, "uid=thomascj,o=princeton university,c=us", "Poiuy123!@#", True)


#server, 'uid=thomascj,o=princeton university,c=us', 'Poiuy123!@#')
#server, 'uid=thomascj,o=princeton university,c=us', 'Poiuy123!@#')