#VMWConfigFile.py

"""
Network, VMware, and general settings for deploying a new Linux VM
"""



"""
General settings
"""
deploy_settings = dict()
deploy_settings["dns_servers"]      = ['8.8.8.8','8.8.4.4']
deploy_settings["port"]             = 443

"""
VCenter settings
"""
vc_settings = dict()
vc_settings["vcenter"] = "10.120.80.10"
vc_settings["datacenter"] = "DC Hornos"
vc_settings["user"] = "administrator@vsphere.local"
vc_settings["password"] = "F1b3rc0rp!"
#vc_settings["resource_pool"] = ""
#vc_settings["dvs"] = "vdSwitch-SLO-HUB-01"
#vc_settings["cluster"] = "Cloud-DCHornos-Interno-01"

# rpool_settings = dict()
# rpool_settings["Interno"] = "RpoolInternoCambiame"   #ToDo: ChangeMe!!!
# rpool_settings["Cliente"] = "RpoolIClienteCambiame" #ToDo: ChangeMe!!!

"""
Storage networks
"""
# ds_settings = dict()
# ds_settings["Interno"] = "DS_InternoCambiame" #ToDo: ChangeMe!!!
# ds_settings["Cliente"] = "DS_InternoCambiame" #ToDo: ChangeMe!!!

