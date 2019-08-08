# Script used to create NewStudent-* tenants
# Run this script to create NewStudent-* tenants
# as well as relevant configuration
# Note: the script is functional, but you may need to implement
# a few changes to satisfy the given task
#
#

# Import access classes
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest

# Import model classes
from cobra.model.fvns import VlanInstP, EncapBlk
from cobra.model.infra import RsVlanNs, AttEntityP, RsDomP
from cobra.model.fv import Tenant, Ctx, BD, RsCtx, Ap, AEPg, RsBd, RsDomAtt, RsPathAtt
from cobra.model.phys import DomP
import json

### Disable SSL Certificate warnings
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

### Setup initial config variables for connecting to the apic
APICURL = 'https://10.1.1.51'
APICADMIN = 'admin'
APICPASS = 'Cciedc01'
TENANTSFILE = 'newStudentTenants.json'
ATTENTITYP = 'Test-AEP'    ## name if the Attached Entity Profile used for Srv5

with open(TENANTSFILE, 'r') as f:  ### open JSON file and load its objects to objList
   objList = json.load(f)

# Connect to APIC
print('Initializing connection to APIC ...')
moDir = MoDirectory(LoginSession(APICURL, APICADMIN, APICPASS))
moDir.login()

# Get the top level Policy Universe Directory
uniMo = moDir.lookupByDn('uni')
uniInfraMo = moDir.lookupByDn('uni/infra')

### Create Physical Domain for All Student Tenants
### fetch first student from json file and use it to create our Physical Domain
#
#  physDomainInst ('name') => Physical Domain Name
#
physDomainObj = objList[0]
physDomainInst = physDomainObj['physDomainInst']
print('Creating Physical Domain \"{}\"..').format(physDomainInst['name'])
physDomPMo = DomP(uniMo, physDomainInst['name'])
physDomCfg = ConfigRequest()
physDomCfg.addMo(physDomPMo)
moDir.commit(physDomCfg)

### Create VLAN Pool for All Student Tenants
### We are reusing VLAN Pool name to be exact same as Physical domain name
print('Creating VLAN Pool \"{}\"..').format(physDomainInst['name'])
fvnsVlanInstPMo = VlanInstP(uniInfraMo, physDomainInst['name'], 'static')
vlanRangeCfg = ConfigRequest()
vlanRangeCfg.addMo(physDomPMo)
moDir.commit(vlanRangeCfg)

### Associate VLAN Pool relationship to Physical Domain
RsVlanNs(physDomPMo, tDn=fvnsVlanInstPMo.dn)
physDomCfg = ConfigRequest()
physDomCfg.addMo(physDomPMo)
moDir.commit(physDomCfg)
print('Linking physical Domain \"{}\" to VLAN Pool \"{}\"..').format(physDomainInst['name'],physDomainInst['name'])

### Link to AttEntityP
### We're adding Physical Domain Relationship to Attached Entity Profile
print('Linking Physical Domain to Attached Entity Profile \"{}\"..').format(ATTENTITYP)
AttEntityPmo = AttEntityP(uniInfraMo, ATTENTITYP)
RsDomP(AttEntityPmo, tDn=physDomPMo.dn)
attEntityCfg = ConfigRequest()
attEntityCfg.addMo(AttEntityPmo)
moDir.commit(attEntityCfg)

# Create Tenants
print ('Starting Creation of Tenants and VLAN Ranges.')

# Iterate over tenants in JSON file
for tenantObj in objList[1:]:
   # Create vlan Range for single Tenant
   # Fetch vlan range Dictionary for JSON
   vlanRange = tenantObj['vlanRange']
   print ('Creating VLAN Range for Student \"{}\"').format(vlanRange['name'])

   # Prepare arguments to be used when creating VLAN range
   # If you need to modify VLAN ranges, ensure to use value returned by vlanRange['from'] or vlanRange['to']
   vlanRangeArgs = {
		'from': 'vlan-' + str(vlanRange['from']+1500),
		'to': 'vlan-' + str(vlanRange['to']+1500),
		'name': vlanRange['name']
      }

   # Intentionally left print statement for debugging if necessary
   # print(vlanRangeArgs)
   # Create VLAN range using parameters defined in vlanRangeArgs
   #
   # vlanRangeArgs['from'] => First VLAN in Range
   # vlanRangeArgs['to'] => Last VLAN in Range
   # vlanRangeArgs['name'] => VLAN Range name

   EncapBlk(fvnsVlanInstPMo,vlanRangeArgs['from'],vlanRangeArgs['to'],vlanRangeArgs['name'])

   # Create config request and commit VLAN Range to APIC
   nsCfg = ConfigRequest()
   nsCfg.addMo(fvnsVlanInstPMo)
   moDir.commit(nsCfg)

   print ('VLAN Range \"{}\" Creation Completed ').format(vlanRange['name'])

   tenant = tenantObj['tenantInst']
   # print tenant name
   print ('Creating Tenant \"{}\"..').format(tenant['name'])
   fvTenantMo = Tenant(uniMo, tenant['name'])

   # Create Private Network under Tenant
   Ctx(fvTenantMo, tenant['ctx'])

  # Create Bridge Domain under Tenant
   fvBDMo = BD(fvTenantMo, name=tenant['bd'])

   # Associate BD to Private Network
   RsCtx(fvBDMo, tnFvCtxName=tenant['ctx'])

  # Create Application Profile under Tenant
   for app in tenant['aps']:
      print ('Creating Application Profile. \"{}\"..').format(app['name'])
      fvApMo = Ap(fvTenantMo, app['name'])
      # Read list of EPGs from JSON and create each EPG under Application Profile
      for epg in app['epgs']:
         print ('Creating EPG: \"{}\" ...').format(epg['name'])

         # Create EPG object fvAEPgMo
         fvAEPgMo = AEPg(fvApMo, epg['name'])

         # Associate EPG to Bridge Domain
         RsBd(fvAEPgMo, tnFvBDName=tenant['bd'])

         # Associate EPG to Physical Domain
         RsDomAtt(fvAEPgMo, physDomPMo.dn)
         RsPathAtt(fvAEPgMo, tDn=epg['path'].replace('paths-100','paths-102'), encap=('vlan-' + str(epg['encap']+1500)), instrImedcy=epg['instrImedcy'], mode=epg['mode'])

   # Commit Tenant to the Configuration
   tenantCfg = ConfigRequest()
   tenantCfg.addMo(fvTenantMo)
   moDir.commit(tenantCfg)

### Logout from APIC
moDir.logout()
print('All done!')
