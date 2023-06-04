#!/usr/bin/bash

SOURCE="./ws0.img"
TARGET=$1
NUMBER=$2
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
# Unmount the drive
umount target

echo "Done."
