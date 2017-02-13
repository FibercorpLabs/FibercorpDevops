from nsxramlclient.client import NsxClient

class getId(object):
	def __init__(self, session):
		self.session = session

	def edges(self):
		edges_config = self.session.read('nsxEdges')
		self.session.view_body_dict(edges_config['body'])

		try:
			for i in range(len(edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary'])):
				r = edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary'][i]
				print r['id'] + " -- " + r['name']
		except KeyError:
			r = edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary']
			print r['id'] + " -- " + r['name']

	def vdnScopes(self):
		vdnScopes = self.session.read('vdnScopes','read')
		#session.view_body_dict(vdnScopes['body'])

		print vdnScopes['body']['vdnScopes']['vdnScope']['name'] + ' -- '
		 + vdnScopes['body']['vdnScopes']['vdnScope']['objectId']

	def virtualWires(self):
		uri_parameters = {}
		uri_parameters = {'scopeId': 'vdnscope-2'}

		vwires = self.session.read('logicalSwitches',uri_parameters)
		self.session.view_body_dict(vwires['body'])
		
		try:
			for i in range(len(vwires['body']['virtualWires']['dataPage']['virtualWire'])):
				vw = vwires['body']['virtualWires']['dataPage']['virtualWire'][i]
				print vw['name'] + " -- " + vw['objectId']

		except KeyError:
			vw = vwires['body']['virtualWires']['dataPage']['virtualWire']
			print vw['name'] + " -- " + vw['objectId']