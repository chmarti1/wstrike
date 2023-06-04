#!/bin/bash

SOURCE=$1
TARGET=$2
NUMBER=$3
HOSTNAME=ws${NUMBER}
PASSWD=`openssl rand -base64 6`

# Force unmount of the drive
umount $TARGET

# Write the source image to the target drive
dd if=$SOURCE of=$TARGET bs=1M status=progress

# If it doesn't exist, make a directory for the target drive
if [ ! -d ./target ]; then
    mkdir target
fi
# Mount the target drive
mount $TARGET ./target
# Set the host name
echo $HOSTNAME > ./target/etc/hostname
sed -i "s/127.0.1.1.*/127.0.1.1\t${HOSTNAME}/" ./target/etc/hosts

# Unmount the drive
umount target

echo "Done."
