from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import requests
import ssl

def vcenter_conn(config):
	host = config['vcenter']['host']
	port = config['vcenter']['port']
	user = config['vcenter']['user']
	password = config['vcenter']['password']

	# Disabling urllib3 ssl warnings
	requests.packages.urllib3.disable_warnings()
	 
	# Disabling SSL certificate verification

	if config['vcenter']['tls_version'] == '1.2':
		ssl_context = ssl.PROTOCOL_TLSv1_2
	elif config['vcenter']['tls_version'] == '1':
		ssl_context = ssl.PROTOCOL_TLSv1_2

	context = ssl.SSLContext(ssl_context)
	context.verify_mode = ssl.CERT_NONE

	try:
		si = None
		try:
			
			si = connect.SmartConnect(host=host,
									  user=user,
									  pwd=password,
									  port=port,
									  sslContext=context)

		except IOError as e:
			pass
			atexit.register(Disconnect, si)

	except vmodl.MethodFault as e:
		print("Caught vmodl fault: %s" % e.msg)
		return None

	except Exception as e:
		print("Caught exception: %s" % str(e))
		return None

	return si

def nsx_conn(config):
	return {'host': config['nsx']['host'],
			'port': config['nsx']['port'],
			'user': config['nsx']['user'],
			'password': config['nsx']['password'] }

ConnMap = {'vcenter': vcenter_conn, 'nsx': nsx_conn}

def conn_method(config, product):
	conn_func = ConnMap[product]
	return conn_func(config)

