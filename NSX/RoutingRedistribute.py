import argparse


from conf import *
from nsxramlclient.client import NsxClient
from ReadEdge import ReadEdge

def get_args():

    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Configure Edge Interfaces')
    parser.add_argument('-id','--edgeId', help='Edge ID',type=str,required=True)
    parser.add_argument('-a','--action', help='Permit or deny',type=str,required=True)
    parser.add_argument('-f','--frm', help='From bgp:connected:isis:ospf:static',type=str,required=True)
    parser.add_argument('-p','--prefix', help='Prefix name',type=str,required=False)
   
    args = parser.parse_args()
    
    return args



def RoutingRedistribute():

	args = get_args()

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	uri_parameters = {}
	uri_parameters = {'edgeId': args.edgeId}

	edge_config = ReadEdge(args.edgeId)

	session.view_body_dict(edge_config['body'])

	
	routing = edge_config['body']['edge']['features']['routing']
	session.view_body_dict(routing)


	routing['bgp']['redistribution']['enabled'] = 'true'
	routing['bgp']['redistribution']['rules'] = {'rule' : {'action': args.action, 'from' : {args.frm : 'true'}, 'prefixName' : args.prefix}}
	
	session.view_body_dict(routing)

	response = session.update('routingConfig',uri_parameters=uri_parameters,request_body_dict={'routing' : routing})
	session.view_response(response)
	
		
def main():


	RoutingRedistribute()


if __name__ == '__main__':
	exit(main())






