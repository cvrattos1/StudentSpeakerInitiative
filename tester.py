import pustatus

serverconnection = pustatus.ServerConnection("ssidev", "Ssidev333:)")
uid = "rdondero"
results = pustatus.isUndergraduate(serverconnection, uid)
results1 = pustatus.isGraduateStudent(serverconnection, uid)
results2 = pustatus.isFaculty(serverconnection, uid)

print(results)
print(results1)
print(results2)                 
               