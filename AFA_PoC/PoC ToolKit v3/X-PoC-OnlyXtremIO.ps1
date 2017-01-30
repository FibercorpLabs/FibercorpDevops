########################################################################
######  EMC - XtremIO | AFA POC Rapid Deployment Utility          ######
######  X-POC (RDU) v3.0 Build 02021600                           ######
######  Author: Steve Kehrer                                      ######
######  Contact: steven.kehrer@emc.com                            ######
######	Last Updated: 02/02/2016                                  ######
########################################################################

Set-PowerCliConfiguration -DisplayDeprecationWarnings $false -Confirm:$false | Out-Null
Set-PowerCliConfiguration -InvalidCertificateAction ignore -Confirm:$false | Out-Null
Set-PowerCliConfiguration -Scope User -ParticipateInCeip $false -Confirm:$false | Out-Null
Set-ExecutionPolicy Bypass -Confirm:$false | Out-Null

# Globals
[console]::ForegroundColor = "White"
$global:run_state = 0
$global:sel_vendor = $null
$global:request = $null
$global:vc_conn_error = $null
$global:array_cfg_comp = $null
$global:vc_cfg_comp = $null
$global:vol_nam_pat = $null
$global:inc_snaps = $null
$global:inc_snaps_comp = $null
$global:num_vols = $null
$global:Xtrem_IG_HBAs = $null
$global:my_IGs = $null
$global:vol_cfg_comp = $null
$global:hba_cfg_comp = $null
$global:vdb_vms_exist = $null
$global:vm_nam_pat = $null
$global:sel_VMs = $null
$global:finished = $null
$global:ack_match = 0
$global:sftp_error = 0

# Create/verify configuration output directory 
cls
$global:conf_dir = "C:\vdbcfg"
$global:sftp_dir = "C:\vdbcfg\sftp"
$global:sftp_test_file = "C:\vdbcfg\sftp\sftp_test.txt"
if (Test-Path $conf_dir) {
	#uncomment line below to begin each run with an empty config by removing all existing config files 
	#del $conf_dir\*.*
} else {
	md C:\vdbcfg | Out-Null
}
if (Test-Path $global:sftp_dir){
	del $global:sftp_dir\*.*
	$test_file = "this is a test" | Out-File $global:sftp_test_file -Encoding utf8
}else {
	md C:\vdbcfg\sftp | Out-Null
	$test_file = "this is a test" | Out-File $global:sftp_test_file -Encoding utf8
}

# Function - acknowldegement code
Function ack_code ($length = 6){
    $digits = 48..57
    $letters = 97..122

    $global:ack_code = get-random -count $length `
        -input ($digits + $letters) |
            % -begin { $aa = $null } `
            -process {$aa += [char]$_} `
            -end {$aa}
	if ($global:ack_match -eq 1){
		Write-Host -fore Yellow "Code mismatch!"
	}
	Write-Host "`nPlease enter the acknowledgement code to continue..."
    Write-Host "`nAcknowledgement Code:" $ack_code
	# enter my code
	$global:my_ack_code = $null
	$global:my_ack_code = Read-Host "          Enter Code"
	While ($global:my_ack_code -ne $global:ack_code){
		$global:ack_match = 1
		ack_code
	}
}

# Function - Replace Write-Host with Write-ColorText to allow multiple color specifcations in a single line
#            Example: Write-ColorText -Blue "this is blue" -Green "this is green" -Red "this is red"
#            This will replace the command Write-Host -fore Blue "this is blue"
function Write-ColorText
{
    $allColors = ("-Black","-DarkBlue","-DarkGreen","-DarkCyan","-DarkRed","-DarkMagenta","-DarkYellow","-Gray","-Darkgray","-Blue","-Green","-Cyan","-Red","-Magenta","-Yellow","-White","-Foreground")
    $color = "Foreground"
    $nonewline = $false

    foreach($arg in $args)
    {
        if ($arg -eq "-nonewline")
        { 
            $nonewline = $true 
        }
        elseif ($allColors -contains $arg)
        {
            $color = $arg.substring(1)
        }
        else
        {
            if ($color -eq "Foreground")
            {
                Write-Host $arg -nonewline
            }
            else
            {
                Write-Host $arg -foreground $color -nonewline
            }
        }
    }

    Write-Host -nonewline:$nonewline
}

# Function - continue any key
function ak2cont {
	Write-Host # empty line
	Write-Host "Press any key to continue..."
	$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function - start function for looping back to start
function start_poc_cfg {
	cls
	banner
	welcome
	pre_req_ck
}

# Function - found configuration data warning
function warn_found {
	Write-Host "_____________________________________________________________________"
	Write-Host "                                                                     " -back Red
	Write-Host "  !!!Warning!!!                                                      " -back Red
	Write-Host "                                                                     " -back Red
	Write-Host "  Existing configuration data was found on the array!                " -back Red
	Write-Host "  This utility should only be used on an empty, unconfigured array.  " -back Red
	Write-Host "  The following configured entities were found:                      " -back Red
	Write-Host "_____________________________________________________________________" -back Red
}

# Function - removing configuration data warning
function warn_remove {
	Write-Host "______________________________________________________________"
	Write-Host "                                                              " -back Red
	Write-Host "  !!!Warning!!!                                               " -back Red
	Write-Host "                                                              " -back Red
	Write-Host "  Preparing to remove all existing configured entities from   " -back Red
	Write-Host "  the selected array. This process is not reversible and may  " -back Red
	Write-Host "  result in data loss. Proceed with extreme caution!          " -back Red
	Write-Host "______________________________________________________________" -back Red
}

# Function - wipe XtremIO configuration
function Xtrem_Clean {
	cls
	banner
	$remove_scheds = (Get-XtremSchedulers).href
	$remove_CGs = (Get-XtremCGs).href
	$get_vol_maps = Get-XtremVolumeMappings -Properties index,name | sort index
	$remove_vols = Get-XtremVolumes -Properties index,name | sort index
	$remove_IGs = (Get-XtremInitiatorGroups).name
	if ($remove_scheds.count -gt 0 -or $remove_CGs.count -gt 0 -or $remove_vols.count -gt 0 -or $remove_IGs.count -gt 0){
		warn_found
		Write-Host # empty line
		if ($remove_vols.count -gt 0){
			Write-Host "  Volumes:" $remove_vols.count
		}
		if ($remove_IGs.count -gt 0){
			Write-Host "  Initiator Groups:" $remove_IGs.count
		}
		if ($remove_CGs.count -gt 0){
			Write-Host "  Consistency Groups:" $remove_CGs.count
		}
		if ($remove_scheds.count -gt 0){
			Write-Host "  Schedulers:" $remove_scheds.count
		}
		# remove existing configuration or exit
		Write-Host -fore Yellow "`nThese entities must be removed before continuing."
		Write-Host -fore Yellow "Would you like to remove the entities now?"
		$remove_cfg = $null
		while ($remove_cfg -ne "y" -and $remove_cfg -ne "n"){
			Write-Host -fore Cyan "`n  Y. [Yes]"
			Write-Host -fore Cyan "  N. [No]`n"
			$remove_cfg = Read-Host "Please select Y or N"
		}
		if ($remove_cfg -eq "y"){
			cls
			banner
			warn_remove
		    ack_code
			if ($remove_scheds.count -gt 0){
				cls
				banner
				Write-Host "Removing existing schedulers...`n"
				foreach ($s in $remove_scheds){
					$s = ($s).split('/')[8]
					$remove_sched = Remove-XtremScheduler -SchedID $s
					Write-Host "Removed scheduler: $s"
				}
			    Write-Host -fore Green "`nSuccessfully removed schedulers."
			}
			sleep 2
			if ($get_vol_maps.count -gt 0){
				cls
				banner
				Write-Host "Removing existing volume mappings...`n"
				foreach ($g in $get_vol_maps){
					$map = Get-XtremVolumeMapping -MappingName ($g).name
					$remove_map = Remove-XtremVolumeMapping -VolumeName ($map)."vol-name" -InitiatorGroupName ($map)."ig-name"
					if (($map)."vol-name" -like "*S1"){
						Write-Host "Removed mapping of" ($map)."vol-name" "from" ($map)."ig-name"
					}else{
						Write-Host "Removed mapping of" ($map)."vol-name" "   from" ($map)."ig-name"
					}	
				}
				Write-Host -fore Green "`nSuccessfully removed volume mappings."
			}
			sleep 2
			if ($remove_CGs.count -gt 0){
				cls
				banner
				Write-Host "Removing existing consistency groups...`n"
				foreach ($cg in $remove_CGs){
					$cg = ($cg).split('/')[8]
					$remove_cg = Remove-XtremCG -CGID $cg
					Write-Host "Removed consistency group:" $cg
				}
				Write-Host -fore Green "`nSuccessfully removed consistency groups."
			}
			sleep 2
			if ($remove_vols.count -gt 0){
				cls
				banner
				Write-Host "Removing volumes...`n"
				foreach ($v in $remove_vols){
					$remove_vol = Remove-XtremVolume -VolumeName ($v).name
					Write-Host "Removed volume:" ($v).name
				}
				Write-Host -fore Green "`nSuccessfully removed volumes."
			}
			sleep 2
			if ($remove_IGs.count -gt 0){
				cls
				banner
				Write-Host "Removing initiator groups...`n"
				foreach ($IG in $remove_IGs){
					$remove_IG = Remove-XtremInitiatorGroup -InitiatorGroupName $IG
					Write-Host "Removed initiator group:" $IG
				}
				Write-Host -fore Green "`nSuccessfully removed initiator groups."
			}
			sleep 2
		}
		if ($remove_cfg -eq "n"){
			Write-Host "`nExiting X-PoC utility!`n"
			exit
		}
	}
}

# Functions - Banner and main_menu_msg
function banner {
	#Write-Host -fore White "____________________________________________________________________________"
	Write-Host -fore White "                                                                            " -Back Blue
	Write-Host -fore White "  EMC - XtremIO | AFA POC Rapid Deployment Utility                          " -Back Blue
	Write-Host -fore White "  X-POC (RDU) v3.0 Build 02021600                                           " -Back Blue
	Write-Host -fore White "____________________________________________________________________________" -Back Blue
	Write-Host # empty line
}

function welcome {
	cls
	banner
	Write-Host "This utility was developed to automate the majority of tasks required"
	Write-Host "for configuring AFA PoC environment. These tasks include:"
	Write-Host # empty line
	Write-Host -fore Cyan "   - Selecting the worker VMs and their hosts"
	Write-Host -fore Cyan "   - Creating array intiator groups and adding initiators"
	Write-Host -fore Cyan "   - Creating LUNs and snapshots"
	Write-Host -fore Cyan "   - Mapping LUNs to initiator groups"
	Write-Host -fore Cyan "   - Mapping LUNs to the worker VMs as RDMs"
	Write-Host -fore Cyan "   - Creating a consistency group (CG) and adding volumes"
	Write-Host -fore Cyan "   - Scheduling CG snapshots"
	Write-Host -fore Cyan "   - Uploading configuration files to the command VM"
	Write-Host # empty line
	Write-Host "Using this tool will streamline the configuration process while"
	Write-Host "greatly reducing the time required to complete the PoC configuration."
	ak2cont
	cls
	banner
	Write-Host -fore white "_________________________________________________________________"
	Write-Host -fore black "                                                                 " -back Yellow
	Write-Host -fore black "  Prerequisites:                                                 " -back Yellow 
	Write-Host -fore black "                                                                 " -back Yellow
	Write-Host -fore black "  Prior to running this utility, please remove any Volumes,      " -back Yellow
	Write-Host -fore black "  Initiator Groups, Consistency Groups & Schedulers from the     " -back Yellow
	Write-Host -fore black "  XtremIO array. This process can be done manually or performed  " -back Yellow
	Write-Host -fore black "  automatically as a function of this utility.                   " -back Yellow
	Write-Host -fore black "                                                                 " -back Yellow
	Write-Host -fore black "  Configuration will fail if the array has existing entities!    " -back Yellow
	Write-Host -fore white "_________________________________________________________________" -back Yellow
	Write-ColorText "`nBefore you continue:"
	Write-Host # empty line
	Write-ColorText -Yellow "   - Ensure hosts are configured according to XtremIO best"
	Write-ColorText -Yellow "     practices including queue depth and MPIO"
	Write-ColorText -Yellow "   - Ensure array is clean as outlined above"
	Write-ColorText -Yellow "   - Perform FC zoning of hosts to array"
	Write-ColorText -Yellow "   - Deploy the AFA PoC VMs"
	Write-ColorText -Yellow "   - Configure a network accessible IP on command VM"
	Write-ColorText -Yellow "   - Download vdbench50403.zip from Oracle"
	ak2cont
	cls
	banner
	Write-Host -fore white "________________________________________________________________________"
	Write-Host -fore black "                                                                        " -back Yellow
	Write-Host -fore black "  Prior to continuing, you are required to enter an acknowlegement      " -back Yellow
	Write-Host -fore black "  code. Entering the acknowledgement code below serves as verification  " -back Yellow
	Write-Host -fore black "  that the prerequisite configuration steps are complete. Furthermore,  " -back Yellow
	Write-Host -fore black "  you acknowledge that any remaining configured entities will be        " -back Yellow
	Write-Host -fore black "  permanently deleted during the configuration process.                 " -back Yellow
	Write-Host -fore black "                                                                        " -back Yellow
	Write-Host -fore black "  This may result in unrecoverable loss of data. PROCEED WITH CAUTION!  " -back Yellow
	Write-Host -fore white "________________________________________________________________________" -back Yellow
	ack_code
	cls
}

# Function - browse for vdbench50403.zip
Function get_vdbench_zip{
	cls
	banner
	Write-Host "The vdbench archive file is required in order to continue.`n"
	Write-Host -fore Cyan "   - If you haven't already done so, download vdbench version 5.04.03 from Oracle"
	Write-Host -fore Cyan "     (http://www.oracle.com/technetwork/server-storage/vdbench-downloads-1901681.html)"
	Write-Host "`nWhen the file is downloaded:`n"
	Write-Host -fore Cyan "   - Press any key to continue"
	Write-Host -fore Cyan "   - Browse to the folder containing the vdbench50403.zip file"
	Write-Host -fore Cyan "   - Select the file and click open"
	ak2cont
	Function Get-FileName($initialDirectory)
	{   
	 [System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") |
	 Out-Null
	
	 $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog
	 $OpenFileDialog.initialDirectory = $initialDirectory
	 $OpenFileDialog.filter = "vdbench Zip file (vdbench*.zip)| vdbench*.zip"
	 $OpenFileDialog.ShowDialog() | Out-Null
	 $global:vdbench_file = $OpenFileDialog.filename
	} #end function Get-FileName
	
	# *** Entry Point to Script ***
	
	Get-FileName -initialDirectory "c:\vdbcfg"
}

# Function - pre-requisite environment checks
function pre_req_ck {
	if ($global:run_state -eq 0){
		setup_vc_conn
		cls
		get_vdbench_zip
		prompt_vms_exist
		cls
		setup_array_conn
		if ($sel_vendor -ne 1){
			Xtrem_Clean
		}
		array_hba_list
		#comp_hbas
		$global:run_state = 1
	}
	if ($global:my_vms.count -lt 1){
		Write-Host -ForegroundColor Yellow "This utility is designed to configure the AFA PoC environment"
		Write-Host -ForegroundColor Yellow "and cannot proceed until the worker VMs have been deployed."
		Write-Host -ForegroundColor Yellow "Please deploy the worker VMs now and proceed when complete."
		Write-Host # empty line
		ak2cont
		pre_req_ck
	}
}

# Function - pre-requisite checks complete and summary display
function pre_comp {
	cls
	banner
	Write-Host -fore Green "Congratulations, the required pre-requisites are complete!`n"
	Write-Host "Selected Worker VMs"
	Write-Host "----------------------------------------"
	foreach ($i in $my_vms) {
			Write-Host -fore Cyan "  $i"
	}
	Write-Host "----------------------------------------"
	Write-Host "Selected Hosts and Initiators"
	Write-Host "----------------------------------------"
	foreach ($i in $global:list_vhbas){
			Write-Host -fore Cyan " "($i).VMHost ($i).wwn
	}
	Write-Host "----------------------------------------"
	ak2cont
}
# Function - configuration menu header message
function main_menu_msg {
	Write-Host "Please select an option from the menu below. Selecting option 1 will"
	Write-Host "guide you through the setup process. All other options will perform a"
	Write-Host "specific configuration function or allow updating previously entered"
	Write-Host "configuration data. When finished, apply the configuration."
	Write-Host -fore Yellow "`nPlease note, when performing configuration manually all steps must be"
	Write-Host -fore Yellow "completed prior to applying the configuration. `n" 
}

# Select array vendor menu
function select_array_vendor {
	Write-Host "Please select the array vendor from the list below.`n"
	$global:sel_vendor = 0
	while ($global:sel_vendor -lt 1 -or $global:sel_vendor -gt 1 ){
		Write-ColorText -Cyan "  1. XtremIO`n"
		Write-ColorText -Cyan "  2. PureStorage`n"
		Write-ColorText -Cyan "  3. SolidFire`n"
		$global:sel_vendor = Read-Host "Please enter a selection"
		Write-Host # empty line
	}
	$global:sel_vendor = [int]$sel_vendor
	switch ($global:sel_vendor){
		1 {
			$global:vendor = "XtremIO"
			$global:ven_init = "xtrem"
		}
		2 {
			$global:vendor = "PureStorage"
			$global:ven_init = "pure"
		}
		3 {
			$global:vendor = "SolidFire"
			$global:ven_init = "solid"
		}
	}
}

# Function - check for array config file
function check_exist_array_cfg {
	$global:array_cfg_out = "c:\vdbcfg\"+$ven_init+"_conn.txt"
	if (test-path $array_cfg_out){
		if ($sel_vendor -ne 1){
		$global:array_mgmt_address = (Get-Content $array_cfg_out)[0]
		}else {
			$global:array_mgmt_address = Get-Content $array_cfg_out
		}
		if ($sel_vendor -ne 2){
		$global:array_mgmt_address = (Get-Content $array_cfg_out)[0]
		}else {
			$global:array_mgmt_address = Get-Content $array_cfg_out
		}
		if ($sel_vendor -ne 3){
		$global:array_mgmt_address = (Get-Content $array_cfg_out)[0]
		}else {
			$global:array_mgmt_address = Get-Content $array_cfg_out
		}
		Write-ColorText "An existing " -Cyan $vendor -White " configuration file was found for connecting"
		Write-ColorText "to the array management address: " -Yellow $array_mgmt_address
		Write-Host "Would you like to import this connection?"
				
		# Choose whether or not to use the detected array configuration file
		$global:use_array_cfg = $null
		while ($use_array_cfg -ne "y" -and $use_array_cfg -ne "n"){
			Write-Host -fore Cyan "`n  Y. [Yes]"
			Write-Host -fore Cyan "  N. [No]`n"
			$global:use_array_cfg = Read-Host "Please select Y or N"
		}
		if ($use_array_cfg -eq "y"){
			Write-Host # empty line
			import_array_cfg
		}
		if ($use_array_cfg -eq "n"){
			Write-Host # empty line
			set_array_conn
		}
	}else {
		set_array_conn
	}
}

# Function - check for vCenter config file
function check_exist_vc_cfg {
	$global:vc_cfg_out = "c:\vdbcfg\vcenter_conn.txt"
	if (test-path $vc_cfg_out){
		$vc_address = (Get-Content $vc_cfg_out)[0]
		Write-Host "An existing VMware configuration file was found for connecting"
		Write-ColorText "to the vCenter server: " -Yellow $vc_address
		Write-Host "Would you like to import this connection?"
		
		# Choose whether or not to use the existing configuration
		$global:use_vc_cfg = $null
		while ($use_vc_cfg -ne "y" -and $use_vc_cfg -ne "n"){
			Write-Host -fore Cyan "`n  Y. [Yes]"
			Write-Host -fore Cyan "  N. [No]`n"
			$global:use_vc_cfg = Read-Host "Please select Y or N"
			Write-Host # empty line
		}
		if ($use_vc_cfg -eq "y"){
			import_vc_cfg
		}else {
			cls
			banner
			set_vc_conn
		}
	}else {
		cls
		banner
		set_vc_conn
	}
}

# Function - verify that address is not empty and reachable
function check_array_address {
	While ($global:array_mgmt_ip -eq [string]::empty){
		Write-Host -fore Yellow "An array management address is required!"
		$global:array_mgmt_ip = Read-Host "Please enter the array management hostname or IP address"
	}
	$global:array_response = Test-Connection -ComputerName $global:array_mgmt_ip -Count 1 -Quiet
	if ($global:array_response -eq $false){
		Write-Host -fore Yellow "The array management address: $array_mgmt_ip is not reachable.`n"
		$global:array_mgmt_ip = Read-Host "Please enter the array management hostname or IP address"
		check_array_address
	}
}

#Function - XtremIO connection error
function xtrem_conn_err {
	Write-Host -fore Yellow "The connection to the XMS: $XtremName was unsuccessful!"
	Write-host -fore Yellow "Please verify that the address and credentials that were"
	Write-host -fore Yellow "entered are correct and try again.`n"
}


function disconnectFlashArray
{
    #a function to disconnect sessions
    add-content $logfile ("Disconnecting FlashArray session(s)")
    foreach ($flasharray in $endpoint)
    {
        Disconnect-PfaArray -Array $flasharray
    }
}


# Function - verify that address is not empty and reachable
function test_array_conn {
	if ($sel_vendor -eq 1){
		New-XtremSession -XmsName $global:XtremName -credlocation C:\vdbcfg | Out-Null
		[int]$array_error = (Get-XtremClusters).error_code
		
		if ($array_error -eq 401){
			cls
			banner
			xtrem_conn_err
			set_array_conn
		}
		$clusters = (Get-XtremClusters).name
		if ($clusters.count -lt 1 -or $clusters -eq $null -or $clusters -eq ""){
			cls
			banner
			xtrem_conn_err
			set_array_conn
		}
	}
	if ($sel_vendor -eq 2){
		try{
			$EndPoint += (New-PfaArray -EndPoint $flasharray -Credentials $Creds -IgnoreCertificateError -ErrorAction stop)
		}
		catch{
			write-host ("Connection to FlashArray " + $flasharray + " failed. Please check credentials or IP/FQDN") -BackgroundColor Red
			write-host $Error[0]
			write-host "Terminating Script" -BackgroundColor Red
			add-content $logfile ("Connection to FlashArray " + $flasharray + " failed. Please check credentials or IP/FQDN")
			add-content $logfile $Error[0]
			add-content $logfile "Terminating Script"
			disconnectFlashArray
			set_array_conn
			
		}
	}
	
	
}

# Function - gather array connection info and export to configuration file
function set_array_conn {
	$global:array_mgmt_ip = Read-Host "Please enter the array management hostname or IP address"
	check_array_address
	$global:array_user = Read-Host "Please enter the username"
	While ($array_user -eq [string]::empty){
		Write-Host -fore Yellow "A username is required!"
		$global:array_user = Read-Host "Please enter the username"
	}
	$global:array_pass = Read-Host "Please enter the password" -AsSecureString
	$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($global:array_pass)
	$global:read_array_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
	While ($read_array_pass -eq ""){
		Write-Host -fore Yellow "A password is required!"
		$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($global:array_pass)
		$global:read_array_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
	}
	
	# Set XtremIO global management parameters
	if ($sel_vendor -eq 1) {
		$global:XtremName = $global:array_mgmt_ip
		$global:XtremUsername = $global:array_user
		$global:XtremPassword = $global:array_pass
		$global:xio_user = "C:\vdbcfg\xiouser.txt"
		$global:xio_pass = "C:\vdbcfg\xiopwd.txt"
		$global:XtremUsername | Set-Content $xio_user
		$global:XtremPassword | ConvertFrom-SecureString | Set-Content $xio_pass
		
		# Create plain text password for use in shell scripts
		$import_pass = Get-Content $xio_pass
	}
	
	if ($sel_vendor -eq 2) {
		$global:PureName = $global:array_mgmt_ip
		$global:PureUsername = $global:array_user
		$global:PurePassword = $global:array_pass
		$global:pure_user = "C:\vdbcfg\pureuser.txt"
		$global:pure_pass = "C:\vdbcfg\purepwd.txt"
		$global:PureUsername | Set-Content $pure_user
		$global:PurePassword | ConvertFrom-SecureString | Set-Content $pure_pass
		
		# Create plain text password for use in shell scripts
		$import_pass = Get-Content $pure_pass
	}




	# Call function to validate the supplied credentials
	test_array_conn

	# Export array connection info to config file
	export_array_conn
}

#Function - export array connection info
function export_array_conn {
	if (test-path $array_cfg_out){
		remove-item $array_cfg_out
	}
	$array_mgmt_ip | out-file $array_cfg_out -Append
	$array_user | out-file $array_cfg_out -Append

	$global:array_cfg_comp = 1
}

# Function - gather VMware vCenter connection info and export to configrration file
function set_vc_conn {
	if ($global:vc_conn_error -eq 1){
		Write-Host -fore Yellow "The connection to the vCenter: $VcServer was unsuccessful!"
		Write-host -fore Yellow "Please verify that the address and credentials that were"
		Write-host -fore Yellow "entered are correct and try again.`n"
	}
	$global:VcServer = Read-Host "Please enter the vCenter hostname or IP address"
	
	# Call function to test if the vCenter address is reachable
	check_vc_address 

	$global:VcUser = Read-Host "Please enter the username"
	While ($VcUser -eq [string]::empty){
		Write-Host -fore Yellow "A username is required!"
		$global:VcUser = Read-Host "Please enter the username"
	}
	$global:VcPwd = Read-Host "Please enter the password" -AsSecureString
	$global:read_vc_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($VcPwd))
	While ($read_vc_pass -eq ""){
		Write-Host -fore Yellow "A password is required!"
		$global:VcPwd = Read-Host "Please enter the password" -AsSecureString
		$global:read_vc_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($VcPwd))
	}
	
	# Call function to test connectivity to vCenter using the supplied info
	test_vc_conn
	

	# Export VC connection info to config file
	export_vc_conn
}

# Function - verify that vCenter address is not empty and reachable
function check_vc_address {
	While ($global:VcServer -eq [string]::empty){
		Write-Host -fore Yellow "A vCenter server address is required!"
		$global:VcServer = Read-Host "Please enter the vCenter hostname or IP address"
	}
	$global:vc_response = Test-Connection -ComputerName $global:VcServer -Count 1 -Quiet
	if ($global:vc_response -eq $false){
		Write-Host -fore Yellow "`nThe vCenter address: $VcServer is not reachable.`n"
		$global:VcServer = Read-Host "Please enter the vCenter hostname or IP address"
		check_vc_address
	}
}

# Function - verify that address is not empty and reachable
function test_vc_conn {
	try {
		Connect-VIServer -Server $VcServer -Username $VcUser -Password $read_vc_pass -ErrorAction:Stop | Out-Null
		$global:vc_conn_error = 0
	}
	Catch {
		$global:vc_conn_error = 1
		cls
		setup_vc_conn
	}
}

# Function - export VC connection info
function export_vc_conn {
	if (test-path $vc_cfg_out){
		remove-item $vc_cfg_out
	}
	$VcServer | out-file $vc_cfg_out -Append
	$VcUser | out-file $vc_cfg_out -Append
	$global:vc_cfg_comp = 1
}

# Function - import array config
function import_array_cfg {
	$array_cfg = get-content -Path $array_cfg_out
	if ($sel_vendor -eq 1) {
		$global:xio_user = "C:\vdbcfg\xiouser.txt"
		$global:xio_pass = "C:\vdbcfg\xiopwd.txt"
		$global:array_mgmt_ip = $array_cfg
		check_array_address
		$global:array_user = Get-Content -Path $xio_user
	} elseif ($sel_vendor -eq 2) {
		$global:pure_user = "C:\vdbcfg\pureuser.txt"
		$global:pure_pass = "C:\vdbcfg\purepwd.txt"
		$global:array_mgmt_ip = $array_cfg
		check_array_address
		$global:array_user = Get-Content -Path $pure_user
	} else {
		$global:array_mgmt_ip = $array_cfg[0]
		$global:array_user = $array_cfg[1]
	}
	Write-ColorText "The username specified in the config file is " -Yellow $array_user -White "."
	Write-ColorText "Proceed with configuration using the imported username " -Yellow $array_user -White "?"
	$global:use_array_user = $null
	While ($use_array_user -ne "y" -and $use_array_user -ne "n"){
		Write-Host -fore Cyan "`n  Y. [Yes]"
		Write-Host -fore Cyan "  N. [No]`n"
		$global:use_array_user = Read-Host "Please select Y or N"
	}
	Write-Host # empty line
	if ($use_array_user -eq "y"){
		# proceed with config using imported user
	}else {
		$global:array_user = Read-Host "Please enter the username"
	}
	# XtremIO specific settings
	if ($sel_vendor -eq 1){
		$global:XtremName = $global:array_mgmt_ip
		$global:XtremUsername = $global:array_user
		$global:array_pass = Read-Host "Please enter the password" -AsSecureString
		$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($global:array_pass)
		$global:read_array_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
		$global:XtremPassword = $global:array_pass
	}
	
	if ($sel_vendor -eq 2){
		$global:PureName = $global:array_mgmt_ip
		$global:PureUsername = $global:array_user
		$global:array_pass = Read-Host "Please enter the password" -AsSecureString
		$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($global:array_pass)
		$global:read_array_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
		$global:PurePassword = $global:array_pass
	}

	# Call function to validate the supplied credentials
	test_array_conn

	# Export updated array connection info to config file
	export_array_conn
}

# Function - import XtremIO SSL certificate
function import_xtremio_cert {
	$xtrem_cert = "C:\vdbcfg\xms_root_ca.crt"	
	if (Test-Path $xtrem_cert) {
		Remove-Item $xtrem_cert	
	}
	$source = "https://$XtremName/xtremapp/xms_root_ca.crt"
	$destination = $xtrem_cert
	Invoke-WebRequest $source -OutFile $destination
	Import-Certificate -FilePath $xtrem_cert -CertStoreLocation Cert:\LocalMachine\Root -Confirm:$false | Out-Null
}

# Function - import vCenter config
function import_vc_cfg {
	$global:vc_cfg_comp = $null
	$vc_cfg = get-content -Path $vc_cfg_out
	$global:VcServer = $vc_cfg[0]
	$global:VcUser = $vc_cfg[1]
	
	# Call function to test if the vCenter address is reachable
	check_vc_address 
	
	Write-ColorText "The username specified in the config file is " -Yellow $VcUser -White "."
	Write-ColorText "Proceed with configuration using the imported username " -Yellow $VcUser -White "?"
	$global:use_vc_user = $null
	While ($use_vc_user -ne "y" -and $use_vc_user -ne "n"){
		Write-Host -fore Cyan "`n  Y. [Yes]"
		Write-Host -fore Cyan "  N. [No]`n"
		$global:use_vc_user = Read-Host "Please select Y or N"
	}
	Write-Host # empty line
	if ($use_vc_user -eq "y"){
		# proceed with config using imported user
	}else {
		$global:VcUser = Read-Host "Please enter the username"
	}
	$global:VcPwd = Read-Host "Password" -AsSecureString
	$global:read_vc_pass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($VcPwd))

	# Call function to test connectivity to vCenter using the supplied info
	test_vc_conn
	
	# Export updated VC connection info to config file
	export_vc_conn

	# Verify connection
	Write-Host -fore Green "`nThe vCenter configuration was imported successfully!"
	$global:vc_cfg_comp = 1
}

# Define XtremIO cluster
function define_cluster {
	Write-Host "`nPlease select the desired cluster from the list below:`n"
	$myClusters = (Get-XtremClusters).name
	$ans = 0
	While ($ans -eq "" -or $ans -eq $null -or $ans -eq 0 -or $ans -gt $myClusters.count){
		$menu = @{}
		for ($i=1;$i -le $myClusters.count;$i++) {
			if ($myClusters.count -gt 1){
				Write-Host -fore Cyan "  $i." $($myClusters[$i-1])
				$menu.Add($i,($myClusters[$i-1]))
			}else{
				Write-Host -fore Cyan "  $i." $myClusters
				$menu.Add($i,$myClusters)
			}
		}
		Write-Host # empty line
		$ans = Read-Host 'Enter selection'
		if ($ans -eq "" -or $ans -eq 0 -or $ans -gt $myClusters.count){
			Write-Host # empty line
		}
	}
	$selection = $menu.Item([int]$ans)
	Write-Host "`nThe"$selection" cluster was selected."
	$global:xtrem_cluster = $selection
	$global:XtremClusterName = $selection
	$global:xtrem_cluster_cfg_comp = 1
}

# Function - Define volume naming pattern
function naming_pattern {
	Write-Host "A naming pattern is required for creating the volumes that will be used"
	Write-Host "during the PoC. Volume names will automatically be appended with a number"
	Write-Host "based on the number of volumes being created. You can use the default"
	Write-Host "volume name, AFA_PoC, or enter a naming pattern manually."
	$global:default_pat = $null
	while ($global:default_pat -ne "y" -and $global:default_pat -ne "n"){
		Write-Host -fore Cyan "`n  Y. [Yes, use default naming pattern, AFA_PoC]"
		Write-Host -fore Cyan "  N. [No, manually enter a naming pattern]`n"
		$global:default_pat = Read-Host "Please select Y or N"
	}
	if ($global:default_pat -eq "y"){
		$global:vol_nam_pat = "AFA_PoC"
	}
	if ($default_pat -eq "n"){
		$ans = $null
		While ($ans -eq $null -or $ans -eq ""){
			$ans = Read-Host "`nPlease enter a naming pattern"
			if ($ans -eq $null -or $ans -eq ""){
				Write-Host -fore Yellow "A volume naming pattern is required to continue!"
			}
		}
		$global:vol_nam_pat = $ans
	}
	# check to ensure volume naming pattern is unique
	$vol_nam_match = $null
	if ($sel_vendor -eq 1){
		define_cluster
		$xtrem_vol_list = (Get-XtremVolumes).name | Sort
		$vol_nam_match += $xtrem_vol_list | where {$_ -like "$global:vol_nam_pat*"}
		if ($vol_nam_match.count -gt 0){
			Write-Host "`nVolumes exist on the specified array that match the entered"
			Write-Host "naming pattern. Please enter a different naming pattern."
			ak2cont
			cls
			banner
			naming_pattern
		}
	} 
}

# Function - Include snapshots in PoC
function include_snaps {
	if ($global:sel_vendor -eq 1) {
		Write-Host "`nWill XtremIO Virtual Copies (XVC) be incorporated into the POC testing?"
	}
	if ($global:sel_vendor -eq 2) {
		Write-Host "`nWill PureStorage Snapshots be incorporated into the POC testing?"
	}
	while ($global:inc_snaps -ne "y" -and $global:inc_snaps -ne "n"){
		Write-Host -fore Cyan "`n  Y. [Yes]"
		Write-Host -fore Cyan "  N. [No]`n"
		$global:inc_snaps = Read-Host "Please select Y or N"
	}
	mk_snap_scripts
	$global:inc_snaps_comp = 1
}

# Function - make snapshot scheduler shell scripts
function mk_snap_scripts {
	if ($global:inc_snaps -eq "y"){
		if ($global:sel_vendor -eq 1){
			$global:snap_start_file = "C:\vdbcfg\sftp\snap_start.sh"
			$global:snap_stop_file = "C:\vdbcfg\sftp\snap_stop.sh"
			if (Test-Path $snap_start_file){
				del $snap_start_file
			}
			if (Test-Path $snap_stop_file){
				del $snap_stop_file
			}
			#make snap start script
			$snap_start = "#!/bin/bash" | Out-File $global:snap_start_file -Encoding utf8
			$snap_start = "curl -k https://" + $global:XtremUsername + ":" + $global:read_array_pass + "@" + $global:array_mgmt_ip + '/api/json/v2/types/schedulers/1 -d ' + "'{" + '"state":"enabled"' + "}'" + " -X PUT" | Out-File $global:snap_start_file -Append -Encoding utf8 -NoNewline
			$global:snap_start_file | Remove-Utf8BOM
			#make snap stop script
			$snap_stop = "#!/bin/bash" | Out-File $global:snap_stop_file -Encoding utf8
			$snap_stop = "curl -k https://" + $global:XtremUsername + ":" + $global:read_array_pass + "@" + $global:array_mgmt_ip + '/api/json/v2/types/schedulers/1 -d ' + "'{" + '"state":"user_disabled"' + "}'" + " -X PUT" | Out-File $global:snap_stop_file -Append -Encoding utf8 -NoNewline
			$global:snap_stop_file | Remove-Utf8BOM
		}
	}
}

# Function - Configure snaps
function conf_snaps {
	$global:num_vols = $num_vols/2
}

# Function - Define number of volumes and size
function xtrem_vol_num_sz {
	# Get cluster size and recommend number of volumes
	if ($global:sel_vendor -eq 1){
		$global:cluster_sz = (Get-XtremCluster)."size-and-capacity"
		[int]$global:XBrick_count = $cluster_sz.split("X")[0]
		[int]$global:XBrick_size = $cluster_sz.split("X").split("TB")[1]
		Write-Host "`nThe selected XtremIO cluster '$xtrem_cluster' contains" $XBrick_count'-'$XBrick_size'TB X-Bricks.'
		if ($XBrick_count -eq 1){
			$global:mk_vols = 16
		}
		if ($XBrick_count -gt 1 -and $XBrick_count -lt 5){
			$global:mk_vols = 32
		}
		if ($XBrick_count -gt 5){
			$global:mk_vols = 64
		}
		Write-Host "Based on the number of X-Bricks in this cluster, the recommended number of volumes is $mk_vols."
		# Menu - accept recommeded volumes or enter new number
		Write-Host "Proceed using the recommended number of volumes?"
		$global:use_vols = $null
		while ($global:use_vols -ne "y" -and $global:use_vols -ne "n"){
			Write-Host -fore Cyan "`n  Y. [Yes, use recommended number of volumes]"
			Write-Host -fore Cyan "  N. [No, enter number of volumes to create]`n"
			$global:use_vols = Read-Host "Please select Y or N"
		}
		if ($global:use_vols -eq "y"){
			$global:num_vols = $mk_vols
		} else {
			$global:num_vols = Read-Host "`nPlease enter the number of volumes to create"
		}
		# Determine cluster useable capacity
		$global:XBrick_usable_cap = (Get-XtremCluster)."ud-ssd-space"/1024/1024/1024
		$XBrick_usable_cap = "{0:F3}" -f $XBrick_usable_cap
		Write-Host "`nThe selected cluster has a useable capacity of" $XBrick_usable_cap'TB.'
		# Define fill percentage
		Write-Host "Please select the desired fill percentage to use during pre-conditioning."
		$ans = $null
		$err_pat = "^[a-zA-z\s]+$"
		while ($ans -match $err_pat -or [int]$ans -lt 1 -or [int]$ans -gt 3 -or $ans -eq "" -or $ans -eq $null){
			Write-Host -fore Cyan "`n  1. 80%"
			Write-Host -fore Cyan "  2. 85%"
			Write-Host -fore Cyan "  3. 90%`n"
			$ans = Read-Host "Please enter the number that corresponds to the desired fill %"
		}
		if ([int]$ans -eq 1){
			$global:fpct = .8
		}
		if ([int]$ans -eq 2){
			$global:fpct = .85
		}
		if ([int]$ans -eq 3){
			$global:fpct = .9
		}
		$global:vol_sz = (([int]$global:XBrick_usable_cap*$global:fpct)*1024)/$global:num_vols
		$global:fpct = $global:fpct*100
		$global:vol_sz = "{0:F0}" -f $global:vol_sz
		$global:vol_cfg_comp = 1
	}else{
		$global:num_vols = Read-Host "`nPlease enter the number of volumes to create"
		
		# Determine cluster useable capacity --- CHANGE ME -- CHANGEME
		$global:XBrick_usable_cap = 10
		
		Write-Host "`nThe selected cluster has a useable capacity of" $XBrick_usable_cap'TB.'
		# Define fill percentage
		Write-Host "Please select the desired fill percentage to use during pre-conditioning."
		$ans = $null
		$err_pat = "^[a-zA-z\s]+$"
		while ($ans -match $err_pat -or [int]$ans -lt 1 -or [int]$ans -gt 3 -or $ans -eq "" -or $ans -eq $null){
			Write-Host -fore Cyan "`n  1. 80%"
			Write-Host -fore Cyan "  2. 85%"
			Write-Host -fore Cyan "  3. 90%`n"
			$ans = Read-Host "Please enter the number that corresponds to the desired fill %"
		}
		if ([int]$ans -eq 1){
			$global:fpct = .8
		}
		if ([int]$ans -eq 2){
			$global:fpct = .85
		}
		if ([int]$ans -eq 3){
			$global:fpct = .9
		}
		$global:vol_sz = (([int]$global:XBrick_usable_cap*$global:fpct)*1024)/$global:num_vols
		$global:fpct = $global:fpct*100
		$global:vol_sz = "{0:F0}" -f $global:vol_sz
		$global:vol_cfg_comp = 1
	
	}
}

# Function - If no IGs found, display error and return to main menu
function no_ig_error {	
	Write-Host -fore Red "No initiator groups were found! Setup cannot continue."
	Write-Host -fore Red "Please configure the appropriate initiator groups on the array"
	Write-Host -fore Red "and re-run the configuration wizard."
	Write-Host "`nPress any key to continue..."
	$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
	cls
	config_menu
}

# Function - get list of all array initiators and initiator groups
function array_hba_list {
	cls
	banner
	#Write-Host "Building the list of array initiators and initiator groups...`n"
	$global:arr_HBAs = $null
	$global:arr_HBAs = @()
	$global:arr_wwns = $null
	$global:arr_wwns = @()
	if ($global:sel_vendor -eq 1){
		$global:Xtrem_HBA_list = $null
		$global:Xtrem_HBA_list += (Get-XtremInitiators).name
		if ($global:Xtrem_HBA_list.count -eq 0 -or $global:Xtrem_HBA_list.count -lt $global:my_vhbas.count){
			# Write-Host -fore Yellow "No initiators have been setup on the selected array, or"
			# Write-Host -fore Yellow "some of the initiators are missing."
			new_IGs
		}
		if ($global:Xtrem_HBA_list.count -eq $global:my_vhbas.count){
			foreach ($i in $global:Xtrem_HBA_list){
				$global:arr_HBAs += Get-XtremInitiator -InitiatorName $i | Select name,port-address,@{Name="ig-id";Expression={($_."ig-id")[1]}}
				$global:arr_wwns += Get-XtremInitiator -InitiatorName $i | Select port-address
			}
			$global:arr_HBAs | sort port-address > $null
			$global:arr_wwns | sort > $null
		}
	}
}

# Function - create initiator groups and map initiators for the required ESXi hosts
function new_IGs {
	cls
	banner
	Write-Host "Creating array initiator groups and initiators..."
	if ($global:sel_vendor -eq 1){
		$global:my_IGs = $null
		$global:my_IGs = @()
		$Octet = '(?:0?0?[0-9]|0?[1-9][0-9]|1[0-9]{2}|2[0-5][0-5]|2[0-4][0-9])'
		[regex] $IPv4Regex = "^(?:$Octet\.){3}$Octet$"
		foreach ($vmhost in $global:my_VM_hosts){
			if ($vmhost -match $IPv4Regex){
				$IGName = ($vmhost).name
			}else{
				$IGName = (($vmhost).name).split('.')[0]
			}
			$new_Xtrem_IG = New-XtremInitiatorGroup -InitiatorGroupName $IGName
			Write-Host # empty line
			Write-Host "Created initiator group: $IGName"
			$global:my_IGs += $IGName
			$IG_Inits = $null
			$IG_inits += $global:list_vhbas | where VMHost -like "$IGName*"
			foreach ($i in $IG_inits){
				$new_ig = New-XtremInitiator -igname $IGName -initname ($IGName + "_" + ($i).Device) -portaddress (($i).wwn -replace '(..)','$1:').trim(':') -initos "esx"
				Write-Host "      Created initiator:" ($IGName + "_" + ($i).Device)
			}
		}
	}
	if ($global:sel_vendor -eq 2){
		$global:my_IGs = $null
		$global:my_IGs = @()
		$Octet = '(?:0?0?[0-9]|0?[1-9][0-9]|1[0-9]{2}|2[0-5][0-5]|2[0-4][0-9])'
		[regex] $IPv4Regex = "^(?:$Octet\.){3}$Octet$"
		foreach ($vmhost in $global:my_VM_hosts){
			if ($vmhost -match $IPv4Regex){
				$IGName = ($vmhost).name
			}else{
				$IGName = (($vmhost).name).split('.')[0]
			}
			#$new_Xtrem_IG = New-XtremInitiatorGroup -InitiatorGroupName $IGName
			New-PfaHost -Array $EndPoint -Name $IGName -ErrorAction stop
			Write-Host # empty line
			Write-Host "Created initiator group: $IGName"
			$global:my_IGs += $IGName
			$IG_Inits = $null
			$IG_inits += $global:list_vhbas | where VMHost -like "$IGName*"
			foreach ($i in $IG_inits){
				#$new_ig = New-XtremInitiator -igname $IGName -initname ($IGName + "_" + ($i).Device) -portaddress (($i).wwn -replace '(..)','$1:').trim(':') -initos "esx"
				Add-PfaHostWwns -Array $EndPoint -Name $IGName -AddWwnList (($i).wwn -replace '(..)','$1:').trim(':') -ErrorAction stop |out-null
				Write-Host "      Created initiator:" ($IGName + "_" + ($i).Device)
			}
		}
	}
	
	
	Write-Host -fore Green "`nSuccessfully created initiator groups."
	sleep 3
	array_hba_list
}

# Function - define HBAs to be used for volume and RDM mapping
function get_xtrem_hbas {
	Write-Host "Please select the desired initiator groups from the list below:`n"
	$Xtrem_IG_ls = (Get-XtremInitiatorGroups).name | Sort
	if ($Xtrem_IG_ls.count -gt 0){
		$global:my_IGs = @()
		$menu = @{}
		$ans = $null
		$err_pat = "^[a-zA-z\s]+$"
		$done = $null
		if ($ans -ne "q") {
			for ($i=1;$i -le $Xtrem_IG_ls.count;$i++) {
				if ($Xtrem_IG_ls.count -gt 1){
					Write-Host -fore Cyan "  $i." $($Xtrem_IG_ls[$i-1])
					$menu.Add($i,($Xtrem_IG_ls[$i-1]))
				}else{
					Write-Host -fore Cyan "  $i." $Xtrem_IG_ls
					$menu.Add($i,$Xtrem_IG_ls)
				}
			}
			Write-Host -Fore Cyan "  Q. Finished"
			$menu.Add($i,"q")
		}
		Write-Host # empty line
		$ans = Read-Host "Enter selection"
		While ($ans -ne "q"){
			if ($ans -match $err_pat -or [int]$ans -lt 1 -or [int]$ans -gt $Xtrem_IG_ls.count){
				Write-Host -fore Red "You have entered an invalid selection."
				if ($global:my_IGs.Count -lt 1){
					Write-Host -fore Red "You must select at least one (1) initiator group to continue."
				}
				Write-Host -fore Red "Please only enter the number that corresponds to the appropriate selection."
				$ans = $null	
			}else {
				if ($global:my_IGs -notcontains $menu.item([int]$ans)){
					$global:my_IGs += $menu.Item([int]$ans)
				}
			}
			$ans = Read-Host "Enter selection"
		}
	
		# Display list of selected IGs
		Write-Host "`nThe following initiator groups have been selected:`n"
		foreach ($i in $global:my_IGs){
			Write-Host -fore Cyan "  $i"
		}

		# Get port addresses of initiators belonging to the selected IGs and export
		foreach ($i in $global:my_IGs) {
			$global:Xtrem_IG_HBAs += Get-XtremInitiators -Properties ig-id,port-address | Where-Object ig-id -like "*$i*"
		}
		$global:Xtrem_IG_HBAs | Select-Object name,port-address
		cls
		banner
		Write-Host "The following initiators are members of the selected initiator groups:`n"
		foreach ($i in $Xtrem_IG_HBAs){
			Write-Host -fore Cyan " "($i).name ($i)."port-address"
		}
		$global:arr_hbas = ($global:Xtrem_IG_HBAs)."port-address"
		Write-Host "`nPress any key to continue..."
		$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
		$global:hba_cfg_comp = 1
	}else{
		no_ig_error
	}
}

# Function - Select XtremIO HBAs
function select_xtrem_hbas {
	if ($array_cfg_comp -ne 1) {
		Write-Host -Fore Yellow "`nAn array connection is required before you can proceed."
		Write-Host -Fore Yellow "Run the array connection setup wizard now?`n"
		$menu = @{}
		$ans = $null
		Write-Host -Fore Cyan "  Y. [Yes]"
		Write-Host -Fore Cyan "  N. [No]`n"
		While ($ans -ne "y" -and $ans -ne "n"){
			$ans = Read-Host "Please enter a selection"
		}
		if ($ans -eq "y"){
			cls
			setup_array_conn
		}else {
			cls
			config_menu
		}
	}
	if ($sel_vendor -eq 1 -and $array_cfg_comp -eq 1 -and $xtrem_cluster_cfg_comp -eq 1){
		get_xtrem_hbas
	}
}

# Function - define and test connection to command VM
function cmd_vm {
	cls
	banner
	$global:cmd_vm_ip = $null
	if ($ip_error -eq 1){
		Write-Host -fore Yellow "The entered IP address is invalid or unreachable!`n"
	}
	if ($global:sftp_error -eq 1){
		Write-Host -fore Yellow "An error occurred while testing the sftp connection to the "
		Write-Host -fore Yellow "command VM. Please check the network and try again.`n"
	}
	Write-Host "Please enter the network accessible IP address assigned"
	Write-Host "to the vdbench command VM:`n"
	$global:cmd_vm_ip = Read-Host "Please enter the IP address"
	if ($global:cmd_vm_ip -eq $null -or $global:cmd_vm_ip -eq ""){
		$ip_error = 1
		cmd_vm
	}else {
		if ($global:cmd_vm_ip -as [ipaddress]){
			$global:cmd_vm_resp = Test-Connection -ComputerName $global:cmd_vm_ip -Count 1 -Quiet
			if ($global:cmd_vm_resp -eq $false){
				cmd_vm
			}else {
				$ip_error = 0
				Write-Host -fore Green "`nThe IP address specified for the command VM is accessible.`n"
				$global:sftp_up = $null
				$global:sftp_up = New-Object -TypeName PSCustomObject -Property @{
					source = $global:sftp_test_file
					target = "tools/"
				}
				Write-Host "Attempting upload of test file to the command VM via SFTP...`n"
				cfg_upload
				if ($global:sftp_error -eq 1){
					cmd_vm
				}
			}
		}else {
			cmd_vm
		}
	}
}

# Function - Select VDB Workers
function prompt_vms_exist {
	cls
	banner
	Write-Host "Beginning the vdbench VM selection process. Please make sure"
	Write-Host "the necessary VMs exist before you continue.`n"
	Write-Host "Have the vdbench VMs been deployed?"
	$global:vdb_vms_exist = $null
	while ($vdb_vms_exist -ne "y" -and $vdb_vms_exist -ne "n"){
		Write-Host -fore Cyan "`n  Y. [Yes]"
		Write-Host -fore Cyan "  N. [No]`n"
		$global:vdb_vms_exist = Read-Host "Please select Y or N"
	}
	if ($vdb_vms_exist -eq "y"){
		cmd_vm
		vm_naming_pattern
	}
	if ($vdb_vms_exist -eq "n"){
		cls
		banner
		Write-Host -fore Yellow "The VDB VMs must be deployed prior to configuration!"
		Write-Host "`nPlease deploy the VMs from the OVA now. After successful"
		Write-Host 'deployment, please select option 6 "Select VDB VMs" from'
		Write-Host "the main menu to proceed with configuration."
		Write-Host "`nPlease press any key to return to the main menu"
	    $x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
	}
}

# Function - define VM naming pattern
function vm_naming_pattern {
	cls
	banner
	$global:vm_nam_pat = $null
	if ($vmrun -eq 1){
		Write-Host -fore Yellow "A VM naming pattern is required...`n"
	}
	Write-Host "Please enter the naming pattern of the worker VMs`n"
	While ($global:vm_nam_pat -eq $null -or $global:vm_nam_pat -eq ""){
		$global:vm_nam_pat = Read-Host("Naming Pattern")
		$vmrun = 1
		if ($global:vm_nam_pat -eq $null -or $global:vm_nam_pat -eq ""){
		vm_naming_pattern	
		}
	}
	$vmrun = 0
	get_vdb_vms
}

# Function - Retrieve a list of VMs matching the defined naming pattern
function get_vdb_vms {
	cls
	banner
	$global:my_VMs = (get-VM).name | Where {$_ -like "$vm_nam_pat*"} | Sort
	if ($global:my_VMs.count -lt 1){
		Write-Host -fore Yellow "No VMs were found matching the naming pattern: $vm_nam_pat"
		vm_naming_pattern		
	}else{
		Write-Host "The following VMs were found matching the pattern:" $vm_nam_pat "`n"
		foreach ($i in $my_vms) {
			Write-Host -fore Cyan "  $i"
		}
		sel_vdb_vms
	}
}

# Function - Select VDB VMs
function sel_vdb_vms {
	Write-Host "`nProceed with the selected VMs?"
	$global:ck_vm_list = $null
	while ($ck_vm_list -ne "y" -and $ck_vm_list -ne "n"){
		Write-Host -fore Cyan "`n  Y. [Yes]"
		Write-Host -fore Cyan "  N. [No]`n"
		$global:ck_vm_list = Read-Host "Please select Y or N"
	}
	if ($ck_vm_list -eq "n" -or $global:my_VMs.count -lt 1){
		vm_naming_pattern
	}else {
		ck_remove_rdms
	}
}

# Function - poweroff VMs
function poweroff_vms {
	$VMsOn = Get-VM -Name ($global:vm_nam_pat + "*") | where { $_.PowerState -eq "PoweredOn"} | Sort
	if ($VMsOn.count -ne 0){
		cls
		banner
		Write-Host -fore Yellow "The worker VMs must be shutdown in order to proceed."
		Write-Host -fore Yellow "`nPowering off the worker VMs...`n"
		foreach ($vm in $VMsOn){
			$vm | Stop-VM -Confirm:$false > $null
			sleep 2
			Write-Host "Powering off" $vm
		}
	sleep 10
	Write-Host -fore Green "`nSuccessfully powered off the worker VMs."
	}
}

# Function - Start VMs
function start_vms {
	$VMsOff = Get-VM -Name ($global:vm_nam_pat + "*") | where { $_.PowerState -eq "PoweredOff"} | Sort
	if ($VMsOff.count -ne 0){
		Write-Host -fore Yellow "Powering on the worker VMs...`n"
		foreach ($vm in $VMsOff){
			$vm | Start-VM -Confirm:$false > $null
			Write-Host "Powering on" $vm
		}
	Write-Host -fore Green "`nSuccessfully powered on the worker VMs."
	sleep 2
	}
}

# Function - check selected VMs for RDMs and allow removal
function ck_remove_rdms {
	# check if RDMs already exist for the selected VMs
	$rdms = $null
	$rdms = @()
    foreach ($vm in $global:my_VMs){
		$rdms += Get-HardDisk -VM $vm -DiskType "RawPhysical"
	}
	if ($rdms.count -gt 0){
		cls
		banner
		$rdms = $null
		$rdms = @()
		Write-Host -fore Yellow "NOTICE - The selected VMs have attached RDM disks!"
		Write-Host "----------------------------------------------------"
		foreach ($vm in $global:my_VMs){
			$rdms = Get-HardDisk -VM $vm -DiskType "RawPhysical"
			if ($rdms.count -ne 0){
				Write-Host $VM " has " $rdms.count " RDMs"
				$rdms = $null
				$rdms = @()
			}
		}
		Write-Host "----------------------------------------------------`n"
		
		# prompt user to remove existing RDMs
		Write-Host "Are you certain the correct VMs were selected?"
		$ans = $null
		while ($ans -ne "y" -and $ans -ne "n"){
			Write-Host -fore Cyan "`n  Y. [Yes]"
			Write-Host -fore Cyan "  N. [No]`n"
			$ans = Read-Host "Please select Y or N"
		}
		if ($ans -eq "n"){
			vm_naming_pattern
		}else {
			Write-Host "`nIt is recommended to remove the existing RDMs before continuing."
			Write-Host "Would you like to remove existing RDMs?"
			$ans = $null
			while ($ans -ne "y" -and $ans -ne "n"){
				Write-Host -fore Cyan "`n  Y. [Yes]"
				Write-Host -fore Cyan "  N. [No]`n"
				$ans = Read-Host "Please select Y or N"
			}
			if ($ans -eq "y"){
				poweroff_vms
				cls
				banner
				$rdms = $null
				$rdms = @()
				Write-Host "Removing RDMs from the selected VMs...`n"
				foreach ($vm in $global:my_VMs){
					$rdms = Get-HardDisk -VM $vm -DiskType "RawPhysical"
					foreach ($i in $rdms){
						Remove-HardDisk -HardDisk $i -DeletePermanently -Confirm:$false
						Write-Host "Removed $i from $vm"
					}
				$rdms = $null
				$rdms = @()
				}
			}
		}
	}
	get_vdb_hosts
}

# Function - get host list from selected VMs
function get_vdb_hosts {
	cls
	banner
	Write-Host "Querying vCenter for the hosts associated with the worker VMs...`n"
	$global:my_VM_hosts = @()
	foreach ($i in $global:my_VMs){
		$global:my_VM_hosts += Get-VMHost -VM $i
	}
	$global:my_VM_hosts = $global:my_VM_hosts | Unique
	get_vhbas
}

# Function - Configure VD Bench VMs
function get_vhbas {
	Write-Host "Building the HBA list for the associated hosts...`n"
	# Get host HBA information and change format from Binary to hex
	$global:my_vhbas = $null
	$global:list_vhbas = @()
	foreach ($i in $global:my_VM_hosts){
		$global:new_vhba = Get-VMhost -Name $i | Get-VMHostHBA -Type FibreChannel | Select VMHost,Device,@{N="WWN";E={"{0:X}" -f $_.PortWorldWideName}} | Sort VMhost,Device
		$global:list_vhbas += $new_vhba | Select VMHost,wwn,Device
		$global:my_vhbas += (($new_vhba).wwn -replace '(..)','$1:').trim(':')
	}
	if ($global:my_vhbas.count -gt 0) {
		Write-Host "The following is the list of hosts and the initiators that"
		Write-Host "correspond to the specified worker VMs:"
		$global:list_vhbas | sort VMHost,Device | Format-Table -autosize
		sleep 3
	}elseif ($global:my_vhbas.count -lt 1) {
		Write-Host -fore Yellow "No HBAs were found for the selected hosts! Please"
		Write-Host -fore Yellow "verify your host configuration and try again."
		ak2cont
	}
}

# Function - Apply VMware host best practices


# Function - Compare HBAs
function comp_hbas {
	if ($global:my_hbas.count -gt $global:arr_wwns.count){
		array_hba_list
	}elseif  ($global:my_hbas.count -eq $global:arr_wwns.count){
		pre_comp
	}
}

# Function - Array Connection Setup
function setup_array_conn {
	banner
	select_array_vendor
	check_exist_array_cfg
}

# Function - vCenter Connection Setup
function setup_vc_conn {
	banner
	check_exist_vc_cfg
}

# Function - Volume Setup
function setup_vols {
	cls
	banner
	naming_pattern
	include_snaps
	xtrem_vol_num_sz
	if ($global:inc_snaps -eq "y"){
		conf_snaps
	}
}

# Function - Apply Configuration
function apply_config {
	cls
	banner
	if ($sel_vendor -eq 1){
		conf_xtremio
	}
	if ($sel_vendor -eq 2){
		conf_purestorage
	}
}

# XtremIO Array Configuration
function conf_xtremio {
	cls
	banner
	Write-Host -NoNewline "Creating volumes"
	if ($global:inc_snaps){
		Write-Host " and snapshots...`n"
	}
	if ($sel_vendor -eq 1){
		$global:Xtrem_vols = $null
		$global:Xtrem_vols = @()
		# Create a new consistency group named AFA_PoC
		$xtrem_cg = "AFA_PoC"
		New-XtremCG -name $xtrem_cg | Out-Null
		foreach ($i in 1..$num_vols){
			$new_vol = New-XtremVolume $vol_nam_pat"."$i $vol_sz'g'
			Write-Host "  Created volume:" $vol_nam_pat"."$i
			$global:Xtrem_vols += ($vol_nam_pat + "." + $i)
			$new_cg_vol = New-XtremCGVol -CG_ID "AFA_PoC" -Vol_Name $vol_nam_pat"."$i | Out-Null
			if ($inc_snaps -eq "y"){
				$new_vol_snap = New-XtremSnapshot -ParentType volume-list -ParentName $vol_nam_pat"."$i -SnapshotSetName ($vol_nam_pat + "." + $i + ".S1") -SnapSuffix "S1" | Out-Null
				Write-Host "Created snapshot:" $vol_nam_pat"."$i".S1"
				$global:Xtrem_vols += ($vol_nam_pat + "." + $i + ".S1")
				$new_cg_vol_snap = New-XtremCGVol -CG_ID "AFA_PoC" -Vol_Name ($vol_nam_pat + "." + $i + ".S1") | Out-Null
			}
		}
		if ($global:inc_snaps -eq "n"){
			Write-Host -fore Green "`nSuccessfully created volumes."
		}else {
			Write-Host -fore Green "`nSuccessfully created volumes and snapshots."
		}
		sleep 3
		cls
		banner
		if ($global:inc_snaps -eq "y"){
			$xtrem_sched = New-XtremScheduler -SchedState "user_disabled" -SchedType "interval" -SchedObjID $xtrem_cg -SchedObjType "ConsistencyGroup" -RetenTime "1d" -SnapInt "0:05:0"
			Write-Host -fore Green "`nVolumes and snapshots were created successfully"
			Write-Host "`nPreparing to map volumes to initiator groups..."
		}else {
			Write-Host -fore Green "`nVolumes were created successfully"
			Write-Host "`nPreparing to map volumes to initiator groups..."
		}
		cls
		banner
		Write-Host "Mapping volumes to initiator groups...`n"
		foreach ($Xtrem_vol in $global:Xtrem_vols){
			foreach ($ig in $global:my_IGs){
				if ($Xtrem_vol -like "*S1"){
					Write-Host "Mapped $Xtrem_vol to $ig"
				}else{
					Write-Host "Mapped $Xtrem_vol    to $ig"
				}
				New-XtremVolumeMapping -VolumeName $Xtrem_vol -InitiatorGroupName $ig > $null
			}
		}
		sleep 10
		Write-Host -fore Green "`nSuccessfully mapped volumes to initiator groups."
	} 
}



# PureStorage Array Configuration
function conf_purestorage {
	cls
	banner
	Write-Host -NoNewline "Creating volumes"
	if ($global:inc_snaps){
		Write-Host " and snapshots...`n"
	}
	if ($sel_vendor -eq 2){
		$global:Xtrem_vols = $null
		$global:Xtrem_vols = @()
		
		# Create a new consistency group named AFA_PoC
		$xtrem_cg = "AFA_PoC"
		
		foreach ($i in 1..$num_vols){
		
			$AuthAction = @{
				password = "pureuser"
				username = "pureuser"
			}
			$ApiToken = Invoke-RestMethod -Method Post -Uri "https://10.120.78.189/api/1.1/auth/apitoken" -Body $AuthAction
			 
			$SessionAction = @{
				api_token = $ApiToken.api_token
			}
			Invoke-RestMethod -Method Post -Uri "https://10.120.78.189/api/1.1/auth/session" -Body $SessionAction -SessionVariable Session
			 
			#Invoke-RestMethod -Method POST -Uri "https://10.120.78.189/api/1.1/volume/${vname}?size=${vSize}" -WebSession $Session
				
			New-PfaVolume -Array $EndPoint -VolumeName $vol_nam_pat"."$i -Unit G -Size $vol_sz		
			Write-Host "  Created volume:" $vol_nam_pat"."$i
			$global:Xtrem_vols += ($vol_nam_pat + "." + $i)

		}
				
		if ($global:inc_snaps -eq "n"){
			Write-Host -fore Green "`nSuccessfully created volumes."
		}else {
			Write-Host -fore Green "`nSuccessfully created volumes and snapshots."
		}
		sleep 3
		cls
		banner
		if ($global:inc_snaps -eq "y"){
			$xtrem_sched = New-XtremScheduler -SchedState "user_disabled" -SchedType "interval" -SchedObjID $xtrem_cg -SchedObjType "ConsistencyGroup" -RetenTime "1d" -SnapInt "0:05:0"
			Write-Host -fore Green "`nVolumes and snapshots were created successfully"
			Write-Host "`nPreparing to map volumes to initiator groups..."
		}else {
			Write-Host -fore Green "`nVolumes were created successfully"
			Write-Host "`nPreparing to map volumes to initiator groups..."
		}
		cls
		banner
		Write-Host "Mapping volumes to initiator groups...`n"
		foreach ($Xtrem_vol in $global:Xtrem_vols){
			foreach ($ig in $global:my_IGs){
				if ($Xtrem_vol -like "*S1"){
					Write-Host "Mapped $Xtrem_vol to $ig"
				}else{
					Write-Host "Mapped $Xtrem_vol    to $ig"
				}
				#New-XtremVolumeMapping -VolumeName $Xtrem_vol -InitiatorGroupName $ig > $null
				Invoke-RestMethod -Method POST -Uri "https://10.120.78.189/api/1.1/hgroup/".$ig"/volume/".$Xtrem_vol -WebSession $Session

			}
		}
		sleep 10
		Write-Host -fore Green "`nSuccessfully mapped volumes to initiator groups."
	} 
}





# Function - map LUNs to workers as RDMs
function map_rdm_luns {
	$global:map_rdms_comp = 0
	cls
	banner
	Write-Host "Preparing the worker VMs for configuration..."
	sleep 10
	$global:naa_ids = $null
	$global:naa_ids = @()
	if ($sel_vendor -eq 1){
		foreach ($i in $global:Xtrem_vols){
			$naa_name = Get-XtremVolume -VolumeName $i | select naa-name
			$naa_id = [string]($naa_name)."naa-name"
			$global:naa_ids += ("naa." + $naa_id)
		}
	}
	if ($sel_vendor -eq 2){
		foreach ($i in $global:Xtrem_vols){
			$volDetails = Invoke-RestMethod -Method GET -Uri "https://10.120.78.189}/api/1.1/volume/${i}" -WebSession $Session
			$rescanHost = $workHost | Get-VMhostStorage -RescanAllHba
			$volNAA = $volDetails.serial
			$volNAA = $volNAA.substring(15)
			$afterLUN = "naa.624*${volNAA}"
			$global:naa_ids += $afterLUN
		}
	}
	
	$devices = $null
	$devices = @()
	$global:devicesPerVM = $global:Xtrem_vols.count/$global:my_VMs.count

	
	#Poweroff VMs
	poweroff_vms

	Write-Host # empty line
	foreach ($vmhost in $global:my_VM_hosts){
		Write-Host "Rescanning HBAs on $vmhost"
		$host_scan = Get-VMHost -Name $vmhost | Get-VMHostStorage -RescanAllHba | Out-Null
	}
	Write-Host -fore Green "`nRescan of host HBAs is complete."
	sleep 2
	cls
	banner
	Write-Host "Preparing to map AFA PoC LUNs to the worker VMs as RDMs...`n"
	Write-Host -fore Yellow "(Please be patient; this process takes a few minutes to complete.)`n"
	$consdevnam = "/vmfs/devices/disks/"
	#foreach ($naa in $global:naa_ids){
	#	$devices += $naa
	#}
	$devicePointer = 0
	foreach ($vmhost in $global:my_VM_hosts){
		$localVMs = Get-VM -location $vmhost -name ($global:vm_nam_pat + "*") | Sort-Object name
		foreach ($localVM in $localVMs){
			$global:scsi_ctrl = $null
			$global:scsi_ctrl = @()
			$flag = 0
			# -DeviceName $devices[$i].ConsoleDeviceName
			for($i=$devicePointer;$i -lt $devicePointer+$devicesPerVM; $i++){
				if ($flag -eq 0 -or ($flag % 4) -eq 0){
					$disk = New-HardDisk -VM $localVM -DeviceName ($consdevnam + $naa_ids[$i]) -DiskType RawPhysical -WarningAction SilentlyContinue
				}
				if ($flag -ne 0 -and $flag -lt 4) {
					$disk = New-HardDisk -VM $localVM -DeviceName ($consdevnam + $naa_ids[$i]) -DiskType RawPhysical -WarningAction SilentlyContinue
					$global:scsi_ctrl += New-ScsiController -HardDisk $disk -BusSharingMode NoSharing -Type ParaVirtual -WarningAction SilentlyContinue
				}
				elseif ($flag -ne 0 -and ($flag % 4) -lt 4) {
					$f = ($flag % 4)
					if ($f -eq 1){
						$disk = New-HardDisk -VM $localVM -DeviceName ($consdevnam + $naa_ids[$i]) -Controller ($global:scsi_ctrl[0]).name -DiskType RawPhysical –Confirm:$false -WarningAction SilentlyContinue
					}																													   						   				   
					if ($f -eq 2){																										   						   				   
						$disk = New-HardDisk -VM $localVM -DeviceName ($consdevnam + $naa_ids[$i]) -Controller ($global:scsi_ctrl[1]).name -DiskType RawPhysical –Confirm:$false -WarningAction SilentlyContinue
					}																													   						   				   
					if ($f -eq 3){																										   						   				   
						$disk = New-HardDisk -VM $localVM -DeviceName ($consdevnam + $naa_ids[$i]) -Controller ($global:scsi_ctrl[2]).name -DiskType RawPhysical –Confirm:$false -WarningAction SilentlyContinue
					}
				}
				$flag+=1
				write-host "Added $disk to $localVM"
			}
			$devicePointer = $devicePointer+$devicesPerVM
		}
	}
	Write-Host -fore Green "`nSuccessfully added RDMs to the worker VMs."
	sleep 2
	#Start VMs
	cls
	banner
	start_vms
	$global:map_rdms_comp = 1
}

# Function - remove the BOM from files 
function Remove-Utf8BOM
{
    [CmdletBinding(SupportsShouldProcess = $true)]
    PARAM(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [System.IO.FileInfo]$File
    )
    BEGIN
    {
        $byteBuffer = New-Object System.Byte[] 3
    }
    PROCESS
    {
        $reader = $File.OpenRead()
        $bytesRead = $reader.Read($byteBuffer, 0, 3)
        if ($bytesRead -eq 3 -and
            $byteBuffer[0] -eq 239 -and
            $byteBuffer[1] -eq 187 -and
            $byteBuffer[2] -eq 191)
        {
            if ($PSCmdlet.ShouldProcess($File.FullName, 'Removing UTF8 BOM'))
            {
                $tempFile = [System.IO.Path]::GetTempFileName()
                $writer = [System.IO.File]::OpenWrite($tempFile)
                $reader.CopyTo($writer)
                $writer.Dispose()
                $reader.Dispose()
                Move-Item -Path $tempFile -Destination $file.FullName -Force
            }
        }
        else
        {
            $reader.Dispose()
        }
    }
}

# Function - afa_prep message
function afa_prep {
	if ($global:map_rdms_comp = 1){
		cls
		banner
		Write-Host -fore Green "AFA PoC automated configuration is complete!"
		Write-Host # empty line
		Write-Host "The AFA PoC environment should now be ready for final configuration." 
		Write-Host "To complete the configuration, please open a terminal session to the"
		Write-Host "command VM and run the afa_prep command (see below):"
		Write-Host # empty line
		Write-ColorText "   " -Yellow "[root@vdb-command ~]#" -White " ./afa_prep -l " $global:devicesPerVM " -n " $global:my_VMs.count " -p " $global:vm_nam_pat " --verbose"
		Write-Host # empty line
		if ($global:inc_snaps -eq "n"){
			Write-Host "The AFA PoC will run the following phases: Fill, Age, Profile & Steady."
		}
		if ($global:inc_snaps -eq "y"){
			Write-Host "The AFA PoC will run the following phases: Fill, Age, Profile,"
			Write-Host "Steady, SnapPrep and SnapSteady."
			Write-Host # empty line
		}
	}
	$global:finished = 1
}

# Function - create the upload package and call the upload script
function mk_sftp_batch{
	$global:sftp_up = $null
	$global:sftp_up = @()
	$global:sftp_up += New-Object -TypeName PSCustomObject -Property @{
		source = $global:vdbench_file
		target = "tools/"
	}
	# add snap_start.sh
	$global:sftp_up += New-Object -TypeName PSCustomObject -Property @{
		source = $global:snap_start_file
		target = "tools/"
	}
	# add snap_stop.sh
	$global:sftp_up += New-Object -TypeName PSCustomObject -Property @{
		source = $global:snap_stop_file
		target = "tools/"
	}

	if ($global:sftp_error -eq 1){
		Write-Host -fore Red "Error uploading files"
		mk_sftp_batch
	}
}

# Function - upload configuration files to command VM
function cfg_upload {
	$global:sftp_error = 0
	try
	{
		# Load WinSCP .NET assembly
		Add-Type -Path "c:\vdbcfg\winscp\WinSCPnet.dll"
 
		# Setup session options
		$sessionOptions = New-Object WinSCP.SessionOptions
		$sessionOptions.Protocol = [WinSCP.Protocol]::Sftp
		$sessionOptions.HostName = $global:cmd_vm_ip
		$sessionOptions.UserName = "root"
		$sessionOptions.Password = "b3nchm4rk"
		$sessionOptions.SshHostKeyFingerprint = "ssh-rsa 2048 e4:21:1d:43:c1:1e:65:67:7e:6a:09:5b:07:2b:6a:6a"
 
		$session = New-Object WinSCP.Session
 
		try
		{
			# Connect
			$session.Open($sessionOptions)
 
			# Upload files
			$transferOptions = New-Object WinSCP.TransferOptions
			$transferOptions.TransferMode = [WinSCP.TransferMode]::Binary
			foreach ($up in $global:sftp_up){
				$transferResult = $session.PutFiles(($up).source, ($up).target, $False, $transferOptions)
			}
	 
			# Throw on any error
			$transferResult.Check()
 
			# Print results
			foreach ($transfer in $transferResult.Transfers)
			{
				Write-Host -fore Green ("Upload of {0} succeeded" -f $transfer.FileName)
				$global:sftp_error = 0
				sleep 2
			}
		}
		finally
		{
			# Disconnect, clean up
			$session.Dispose()
		}
	}
	catch [Exception]
	{
		Write-Host $_.Exception.Message
		$global:sftp_error = 1
	}
}

# Remote SSH executable and arguments
$rem_ssh = "C:\Program Files (x86)\PuTTY\plink.exe"
$rem_ssh_arg1 = "-v" #this argument displays verbose messages associated with the remote ssh command
$rem_ssh_arg2 = "-ssh" #this argument controls the protocol being used

# Display welcome message and perform initial pre-requisite checks
function poc_config {
	welcome
	pre_req_ck
	setup_vols
	apply_config
	map_rdm_luns
	mk_sftp_batch
	cfg_upload
	afa_prep
}
poc_config
Disconnect-ViServer -Server * -Force -Confirm:$false
Remove-XtremSession