import requests
import json

def get_all_edges(conn):

	url = "https://" + conn['host'] + "/api/4.0/edges"
	auth = (conn['user'], conn['password'])
	rheaders = {'Accept': 'application/json'}
	r = requests.get(url, auth=auth, verify=False, headers=rheaders)
	r.raise_for_status()
	r_dict = json.loads(r.text)	
	allEdges = r_dict['edgePage']['data']
	return allEdges