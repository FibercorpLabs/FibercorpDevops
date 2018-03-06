#!/bin/bash

echo "Setting permissions"
chmod -R -f 777 /root/tools
chmod -R -f 777 /root/AFA
chmod 777 "/root/vdbench/linux/config.sh"

ssh root@vdb-001 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-002 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-003 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-004 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-005 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-006 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-007 chmod 777 "/root/vdbench/linux/config.sh"
ssh root@vdb-008 chmod 777 "/root/vdbench/linux/config.sh"

snapstart="/root/tools/snap_start.sh"
snapstop="/root/tools/snap_stop.sh"
if [ -a "$snapstart" ]; then
    sed -i -e 's/\r$//' $snapstart
fi
if [ -a "$snapstop" ]; then
    sed -i -e 's/\r$//' $snapstop
fi
echo "Permissions set successfully"

