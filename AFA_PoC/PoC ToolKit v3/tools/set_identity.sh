#!/bin/bash

if [[ -f ~/.identified ]]
then
    ans="N"
    echo "This system appears to have been previously configured via this script." 
    echo -n "Are you sure you want to search for a new name and IP address? (Y/N) : "
    read -t 30 -n 1 ans
    case $ans in  
	y|Y) 
	    echo ""
	    echo "Proceding with identification..."
	    ;; 
	*) 
	    echo ""
	    echo "Aborting identification."
	    exit 1
	    ;; 
    esac 
fi

ips=( `grep vdb- /etc/hosts | awk '{print $1}'` )
len=${#ips[@]}

declare -i i=0
pingresult=$( ping -c 10 -i 0.5 -q -w 5 ${ips[$i]} | grep '100% packet loss' )

until [[ "$pingresult" != '' || "$i" -ge "$len" ]]; do
    name=$( grep ${ips[$i]} /etc/hosts | awk '{print $2}' )
    echo "Found $name at IP address ${ips[$i]}"
    i+=1
    if (( $i < $len )) 
    then
	pingresult=$( ping -c 10 -i 0.5 -q -w 5 ${ips[$i]} | grep '100% packet loss' )
    fi
done

if (( $i < $len )) 
then
    name=$( grep ${ips[$i]} /etc/hosts | awk '{print $2}' )
    echo "First available slot is $name at IP address ${ips[$i]}"
    [[ -f /etc/sysconfig/network-scripts/ifcfg-eth0 ]] && cp /etc/sysconfig/network-scripts/ifcfg-eth0 /etc/sysconfig/network-scripts/orig-eth0
    cat <<EOF > /etc/sysconfig/network-scripts/ifcfg-eth0
DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=no
BOOTPROTO=static
NAME="System eth0"
IPADDR=${ips[$i]}
NETMASK=255.255.255.0
EOF
    hostnamectl set-hostname $name
    systemctl restart network
    touch ~/.identified
else
    echo "Could not find a free name and IP address to use for this VM."
fi
