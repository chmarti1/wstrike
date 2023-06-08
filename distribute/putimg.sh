#!/bin/bash

SOURCE=$1
TARGET=$2
NUMBER=$3
HOSTNAME=ws${NUMBER}
TARGETFS=${TARGET}p2
TARGETBASE=`basename ${TARGET}`
# Check whether the local machine is using legacy sdXX naming
if [[ ${TARGETBASE} == sd* ]]; then
	TARGETFS=${TARGET}2
fi

PASSWD=`openssl rand -base64 6`

echo "Write file ${SOURCE} to device ${TARGET} with name ${HOSTNAME}."
echo "  We will expect the system partition to be ${TARGETFS}"
echo -n "Are you sure? (y/n):"
read go
if [ ! ${go} = "y" ]; then
    echo "Halting."
    exit 0
fi

# Force unmount of the drive
umount ${TARGET}*

# Write the source image to the target drive
# If this is a file zipped by gzip
if [[ ${SOURCE} == *.gz ]]; then
    gunzip -c ${SOURCE} | dd conv=sparse of=$TARGET bs=1M status=progress
else
    dd conv=sparse if=$SOURCE of=$TARGET bs=1M status=progress
fi

# If it doesn't exist, make a directory for the target drive
if [ ! -d ./target ]; then
    mkdir target
fi

echo "Mounting Filesystem: ${TARGETFS}"
# Mount the target drive
mount $TARGETFS ./target

echo "Changing the host name to ${HOSTNAME}."
# Set the host name
echo $HOSTNAME > ./target/etc/hostname
sed -i "s/127.0.1.1.*/127.0.1.1\t${HOSTNAME}/" ./target/etc/hosts
# Remove the log files if they're there
LOGFILE=./target/var/local/wstrike/wstrike.log
if [ -f ${LOGFILE} ]; then
    echo "Removing file ${LOGFILE}"
    rm ${LOGFILE}
fi
LOGFILE=./target/var/local/wstrike/wsadmin.log
if [ -f ${LOGFILE} ]; then
    echo "Removing file ${LOGFILE}"
    rm ${LOGFILE}
fi

# Unmount the drive
umount target

echo "Done."
