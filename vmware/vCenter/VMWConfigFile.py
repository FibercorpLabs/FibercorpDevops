#VMWConfigFile.py

"""
Network, VMware, and general settings for deploying a new Linux VM
"""




"""
VCenter settings
"""
vc_settings = dict()
vc_settings["vcenter"] = "10.120.110.6"
vc_settings["datacenter"] = "LAB"
vc_settings["resource_pool"] = ""
vc_settings["dvs"] = "LAB_dVS01"
vc_settings["cluster"] = "FC-LAB"

rpool_settings = dict()
rpool_settings["Interno"] = "RpoolInternoCambiame"   #ToDo: ChangeMe!!!
rpool_settings["Cliente"] = "RpoolIClienteCambiame" #ToDo: ChangeMe!!!

"""
Storage networks
"""
ds_settings = dict()
ds_settings["Interno"] = "DS_InternoCambiame" #ToDo: ChangeMe!!!
ds_settings["Cliente"] = "DS_InternoCambiame" #ToDo: ChangeMe!!!

