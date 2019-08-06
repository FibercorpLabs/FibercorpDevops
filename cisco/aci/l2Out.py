#!/usr/bin/env python

# list of packages that should be imported for this code to work
import csv
import cobra.model.l2ext

from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest
from cobra.internal.codec.xmlcodec import toXMLStr
from cobra.model.fvns import VlanInstP, EncapBlk
from cobra.model.infra import RsVlanNs, AttEntityP, RsDomP
from cobra.mit.request import ClassQuery, DnQuery
from cobra.model.fv import Tenant, Ctx, BD, RsCtx, Ap, AEPg, RsBd, RsDomAtt, RsPathAtt

### Disable SSL Certificate warnings
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

apicUrl = 'https://10.120.1.32'
apicUsername = 'admin'
apicPassword = 'F1b3rc0rp'
csvfile  = "/Users/arielik/OneDrive - lsia.fi.uba.ar/Laboral/ACI/data.csv"
vrfName = "VRF_HOUSING"


loginSession = LoginSession(apicUrl, apicUsername, apicPassword)

# Create a session with the APIC and login
moDir = MoDirectory(loginSession)
moDir.login()

# Start at the Top of tenant tree
fvTenantMo = moDir.lookupByDn("uni/tn-PROD-HOR")

#Gather Phys Domain
physMo = moDir.lookupByDn("uni/phys-PHY-DC-HOR")
l2Mo = moDir.lookupByDn("uni/l2dom-DOM_L2OUT")

#Create Application
fvApMo = Ap(fvTenantMo, "HOR-Housing")

f = open(csvfile, 'rb')
reader = csv.reader(f)
for row in reader:
    if row[0] is not "":
        # print row[0] #vlan
        print "Creating " + row[1] #name
        # print row[2] #bd name

        #Create Bridge Domains
        bdName = row[2] + "-BD"
        # print bdName
        fvBDMo = BD(fvTenantMo, name=bdName, arpFlood="yes",multiDstPktAct="bd-flood", unkMcastAct="flood", unkMacUcastAct="flood", ipLearning="no",unicastRoute="no" )

        # Associate BD to Private Network (aka VRF)
        RsCtx(fvBDMo, tnFvCtxName=vrfName)

        #Create EPG
        epgName = row[2] + "-EPG"
        fvAEPgMo = AEPg(fvApMo, epgName)

        # Associate EPG to Bridge Domain
        RsBd(fvAEPgMo, tnFvBDName=bdName)

        # Associate EPG to Physical Domain & L2-Dom
        RsDomAtt(fvAEPgMo, physMo.dn)
        RsDomAtt(fvAEPgMo, l2Mo.dn)

tenantCfg = ConfigRequest()
tenantCfg.addMo(fvTenantMo)
moDir.commit(tenantCfg)


#Create L2 Outside
f = open(csvfile, 'rb')
reader = csv.reader(f)
for row in reader:
    if row[0] is not "":
        l2outName = "L2Out-VL" + row[0]
        l2extOut = cobra.model.l2ext.Out(fvTenantMo, ownerKey=u'', targetDscp=u'unspecified', name=l2outName, descr=u'', ownerTag=u'')
        l2extLNodeP = cobra.model.l2ext.LNodeP(l2extOut, ownerKey=u'', tag=u'yellow-green', name=u'L2Out-Node', descr=u'', ownerTag=u'')
        l2extLIfP = cobra.model.l2ext.LIfP(l2extLNodeP, ownerKey=u'', tag=u'yellow-green', name=u'L2Out-Interface', descr=u'', ownerTag=u'')
        
        l2extRsPathL2OutAtt = cobra.model.l2ext.RsPathL2OutAtt(l2extLIfP, tDn=u'topology/pod-1/protpaths-101-102/pathep-[VPC_for_L2OUT-N7K]', descr=u'', targetDscp=u'unspecified')
        
        l2DomainName = "DOM_L2OUT"
        l2UniDomainName = "uni/l2dom-" + l2DomainName
        l2extRsL2DomAtt = cobra.model.l2ext.RsL2DomAtt(l2extOut, tDn=l2UniDomainName)
        
        vlanId = "vlan-" + row[0]
        bdName = row[2] + "-BD"
        l2extRsEBd = cobra.model.l2ext.RsEBd(l2extOut, encap=vlanId, tnFvBDName=bdName)
        l2OutEpgName = "L2Out-VL" + row[0] + "-EXT_EPG"
        l2extInstP = cobra.model.l2ext.InstP(l2extOut, prio=u'unspecified', matchT=u'AtleastOne', name=l2OutEpgName, descr=u'', targetDscp=u'unspecified')

c = cobra.mit.request.ConfigRequest()
c.addMo(fvTenantMo)
moDir.commit(c)



