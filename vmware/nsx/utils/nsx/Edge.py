import json
from utils.common.Jinja import Jinja
from utils.nsx.NsxRest import NsxRest


class Edge:
    def __init__(self, nsx_rest: NsxRest):
        self.nsx_rest = nsx_rest
    
    def nsx_edge_get_all(self):
        r = self.nsx_rest.nsxGet("/api/4.0/edges", "json")
        r_dict = json.loads(r)
        allEdges = r_dict['edgePage']['data']
        edges = {"edges" : []}
        for edge in allEdges:
            edges["edges"].append({'name' : edge['name'], 'id' : edge['id']})
        return edges
    
    def nsx_edge_get_id_by_name(self, name: str):
        r = nsxGet("/api/4.0/edges", "json")
        r_dict = json.loads(r)
        allEdges = r_dict['edgePage']['data']
        for edge in allEdges:
            if edge['name'] == name:
                return edge['id']
        return ""
    
    def nsx_edge_get_by_name(self, edge_name: str):
        edge_id = nsx_edge_get_id_by_name(edge_name)
        
        return nsx_edge_get_by_id(edge_id)
    
    def nsx_edge_get_by_id(self, edge_id: str):
        r = nsxGet("/api/4.0/edges/" + edge_id, "json")
        r_dict = json.loads(r)
        return r_dict
    
    # NSX_EDGE_CREATION_DELETION
    def nsx_edge_create(self, jinja_vars):
        nsx_edge_xml = os.path.join(os.path.dirname(__file__), '../../templates/edge/nsx_edge_create.j2')
        return self.nsx_rest.nsxPost("/api/4.0/edges", Jinja.render(nsx_edge_xml, jinja_vars), "xml")
    
    def nsx_edge_delete_by_id(self, edge_id):
        return nsxDelete("/api/4.0/edges/" + edge_id, "xml")
    
    def nsx_edge_delete_by_name(self, edge_name):
        edge_id = nsx_edge_get_id_by_name(edge_name)
        return nsx_edge_delete_by_id(edge_id)

    def nsx_edge_update(self, edge_id, jinja_vars):
        data = json.dumps(jinja_vars)
        return nsxPut("/api/4.0/edges/" + edge_id, data, "xml")
    
    def nsx_edge_rename(self, edge_id, name):
        jinja_vars = get_nsx_edge(edge_id)
        jinja_vars['name'] = name
        
        return update_nsx_edge(edge_id, jinja_vars)
    
    def nsx_edge_resize(self, edge_id, applianceSize):
        jinja_vars = get_nsx_edge(edge_id)
        jinja_vars['appliances']['applianceSize'] = applianceSize
        data = json.dumps(jinja_vars)
        
        return update_nsx_edge(self, edge_id, jinja_vars)

    def nsx_edge_get_cli_settings(self, edge_id):
        r = get_nsx_edge(edge_id)
        return r['cliSettings']
    
    def nsx_edge_update_cli_settings(self, edge_id, query_params):
        data = json.dumps(query_params)
        return nsxPut("/api/4.0/edges/" + edge_id + "/clisettings", data, "xml")
    
    def nsx_edge_set_user_and_password(self, edge_id, new_user, new_password):
        query_params = get_cli_settings(edge_id)
        query_params['userName'] = new_user
        query_params['password'] = new_password
        
        return update_cli_settings(self, edge_id, query_params)
    
    def nsx_edge_set_ssh_login_banner(self, edge_id, banner):
        query_params = get_cli_settings(edge_id)
        query_params['sshLoginBannerText'] = banner
        
        return nsx_edge_update_cli_settings(self, edge_id, query_params)
    
    def get_remote_access_status(edge_id):
        clisettings = nsx_edge_get_cli_settings(edge_id)
        
        return clisettings['remoteAccess']
    
    
    def enable_remote_access(edge_id):
        return nsxPost("/api/4.0/edges/" + edge_id + "/cliremoteaccess?enable=True","", "xml")
    
    
    def disable_remote_access(edge_id):
        return nsxPost("/api/4.0/edges/" + edge_id + "/cliremoteaccess?enable=False", "", "xml")
    
    # DNS_CLIENT
    def get_dns_client(edge_id):
        r = nsxGet("/api/4.0/edges/" + edge_id + "/dnsclient", "xml")
        return json.loads(r)
    
    def update_dns_client(edge_id, jinja_vars):
        dir = os.path.dirname(__file__)
        nsx_dns_xml = os.path.join(dir, '../../templates/edge/nsx_edge_dnsclient.j2')
        data = render(nsx_dns_xml, jinja_vars)
        
        return nsxPost("/api/4.0/edges/" + edge_id + "/dnsclient", data, "xml")
    
    def update_primary_dns(edge_id, primary_dns):
        jinja_vars = {'dnsClient' : {'primary_dns' : primary_dns}}
        
        return update_dns_client(edge_id, jinja_vars)
    
    def update_secondary_dns(edge_id, secondary_dns, domain_name):
        return update_dns_client(edge_id, {'dnsClient' : {'secondary_dns' : secondary_dns, 'domain_name' : domain_name}})

    def get_nsx_edge_nat(self, edge_id):
        return self.nsx_rest.nsxGet("/api/4.0/edges/" + edge_id + "/nat/config", "xml")
    
    def update_nsx_edge_nat(edge_id, jinja_vars):
        dir = os.path.dirname(__file__)
        nsx_nat_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_nat.j2')
        data = render(nsx_nat_xml, jinja_vars)
        
        return nsxPost("/api/4.0/edges/" + edge_id + "/nat/config", data, "xml")
    
    def delete_nsx_edge_nat(edge_id):
        return nsxDelete("/api/4.0/edges/" + edge_id + "/nat/config", "xml")
    