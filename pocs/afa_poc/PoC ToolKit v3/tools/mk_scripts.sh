#!/bin/bash

phasefile="/root/AFA/phases.vdb"

function phasefile {
    if [ -a "$phasefile" ]; then
        rm -f $phasefile
    fi
}

function phases {
    echo "1 fill" >> $phasefile
    echo "2 age" >> $phasefile
    echo "3 profile" >> $phasefile
    echo "4 steady" >> $phasefile
}

function snaps {
    echo "5 snapprep" >> $phasefile
    echo "6 snapsteady" >> $phasefile
}

function nosnaps {
    echo "#5 snapprep" >> $phasefile
    echo "#6 snapsteady" >> $phasefile
}

function snapscripts {
	snapstart="/root/tools/snap_start.sh"
	snapstop="/root/tools/snap_stop.sh"
	if [ -a $snapstart ]; then
	    echo "***************************************************************"
		echo "A snap start script exists. If you ran the X-PoC utility,"
		echo "no action is required. Otherwise, please modify the file"
		echo "$snapstart with relevant commands"
		echo "for the array being tested."
	else
		echo "#!/bin/bash" >> $snapstart
		echo "" >> $snapstart
		echo "### XtremIO example - this will interact with the XtremIO REST API to start a snapshot scheduler" >> $snapstart
		echo "### In this example, a consistency group was created, volumes were added to the consistency group" >> $snapstart
		echo "### and a scheduler was created for the consistency group. The scheduler was created in a disabled" >> $snapstart
		echo "### state. This script is called at the beginning of the snapsteady phase and enables the scheduler." >> $snapstart
		echo "" >> $snapstart
		echo "### Example - curl -k https://admin:Xtrem10@10.0.0.50/api/json/v2/types/schedulers/1 -d '{"state":"enabled"}' -X PUT" >> $snapstart
		echo "" >> $snapstart
		echo "### For non-XtremIO arrays, consult the array CLI reference or API guide for how to manage snapshots." >> $snapstart
		echo "### For arrays that support SSH, remote SSH commands can be issued." >> $snapstart
		echo "" >> $snapstart
		echo "### Example - ssh root@10.0.0.50 -pw Password1! enter array command with arguments" >> $snapstart
		echo "***************************************************************"
		echo "Successfully created the snap_start.sh script. Please modify the"
		echo "file with the relevant commands for the array being tested."
	fi
	if [ -a $snapstop ]; then
	    echo "***************************************************************"
		echo "A snap stop script exists. If you ran the X-PoC utility,"
		echo "no action is required. Otherwise, please modify the file"
		echo "$snapstop with relevant commands"
		echo "for the array being tested."
	else
		echo "#!/bin/bash" >> $snapstop
		echo "" >> $snapstop
		echo "### XtremIO example - this will interact with the XtremIO REST API to stop a snapshot scheduler" >> $snapstop
		echo "### In this example, a consistency group was created, volumes were added to the consistency group" >> $snapstop
		echo "### and a scheduler was created for the consistency group. The scheduler was created in a disabled" >> $snapstop
		echo "### state. This script was called at the beginning of the snapsteady phase and enabled the scheduler." >> $snapstop
		echo "### This script is called at the end of snapsteady and will disable the scheduler." >> $snapstop
		echo "" >> $snapstop
		echo "### Example - curl -k https://admin:Xtrem10@10.0.0.50/api/json/v2/types/schedulers/1 -d '{"state":"user_disabled"}' -X PUT" >> $snapstop
		echo "" >> $snapstop
		echo "### For non-XtremIO arrays, consult the array CLI reference or API guide for how to manage snapshots." >> $snapstop
		echo "### For arrays that support SSH, remote SSH commands can be issued." >> $snapstop
		echo "" >> $snapstop
		echo "### Example - ssh root@10.0.0.50 -pw Password1! enter array command with arguments" >> $snapstop
		echo "***************************************************************"
		echo "Successfully created the snap_stop.sh script. Please modify the"
		echo "file with the relevant commands for the array being tested."
	fi
}

function menu {
    echo "Preparing to create the phases file..."
    sleep 1
    read -p "Include snapshot testing phases (y/n)? " choice
    case "$choice" in
        y|Y ) 
            phases
            snaps
            success
            mksnaps="1" ;;
        n|N ) 
            phases
            nosnaps
            success
            mksnaps="0" ;;
        * ) menu ;;
    esac
}

function success {
	echo "The phases.vdb file was created successfully"
}

phasefile
menu
if [ $mksnaps = "1" ]; then
    snapscripts
else
	exit
fi