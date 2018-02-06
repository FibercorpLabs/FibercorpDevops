from nsxramlclient.client import NsxClient

class getId(object):
	def __init__(self, session):
		self.session = session

	def edges(self):
		edges_config = self.session.read('nsxEdges')
		
		try:
			for i in range(len(edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary'])):
				r = edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary'][i]
				print r['id'] + " -- " + r['name']
		except KeyError:
			r = edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary']
			print r['id'] + " -- " + r['name']

	def vdnScopes(self):
		vdnScopes = self.session.read('vdnScopes','read')
		
		print vdnScopes['body']['vdnScopes']['vdnScope']['name'] + ' -- ' + vdnScopes['body']['vdnScopes']['vdnScope']['objectId']

	def virtualWires(self):
		uri_parameters = {}
		uri_parameters = {'scopeId': 'vdnscope-2'}

		vwires = self.session.read('logicalSwitches',uri_parameters)
				
		try:
			for i in range(len(vwires['body']['virtualWires']['dataPage']['virtualWire'])):
				vw = vwires['body']['virtualWires']['dataPage']['virtualWire'][i]
				print vw['name'] + " -- " + vw['objectId']

		except KeyError:
			vw = vwires['body']['virtualWires']['dataPage']['virtualWire']
			print vw['name'] + " -- " + vw['objectId']

	def readVW(self, virtualWireID):
		uri_parameters = {'virtualWireID': virtualWireID}

		response = self.session.read('logicalSwitch', uri_parameters)
		
		return response['body']
