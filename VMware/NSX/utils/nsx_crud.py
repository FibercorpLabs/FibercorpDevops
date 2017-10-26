from nsx_rest import *
import json
from pprint import pprint

#nsxGet('/api/2.0/services/vcconfig')




#TODO RETURN LIST as json
def getAllTZ():
  r = nsxGet("/api/2.0/vdn/scopes")

  # r_dict = json.loads(r)
  # # pprint(r_dict)
  
  # allScopes = r_dict['allScopes']
  # for elem in allScopes:
  #   print elem['id'] + " " + elem['name']
  return r


#Return VDNScope for a give TZ name
#Example: getTZ("GLOBAL-TZ-LAB")
def getTZ(name):
  r = nsxGet("/api/2.0/vdn/scopes")

  r_dict = json.loads(r)
  # pprint(r_dict)
  
  allScopes = r_dict['allScopes']
  for elem in allScopes:
    if name ==elem['name']:
    	print  elem['id']
    	return  elem['id']
    else:
    	return ""


#TODO: def createTZ(name)

#Example: createLS("some","GLOBAL-TZ-LAB")
def createLS(name,tzone, tenantId=""):
  xml_LS = "<virtualWireCreateSpec> \
  <name>" + name + "</name>\
  <tenantId>" + tenantId + "</tenantId>\
  </virtualWireCreateSpec>"

  vdnScope = getTZ(tzone)
  nsxPost("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires",xml_LS)


def getLS(tzone):
  vdnScope = getTZ(tzone)
  return nsxGet("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires")
  



createLS("some","GLOBAL-TZ-LAB")
getLS("GLOBAL-TZ-LAB")



