#!/usr/bin/bash

SOURCE="./ws0.img"
TARGET=$1
NUMBER=$2
PASSWD=`openssl rand -base64 6`

# Force unmount of the drive
umount $TARGET

# Write the source image to the target drive
dd if=$SOURCE of=$TARGET bs=1M status=progress

# Mount the drive
if [[ ! -d ./target ]]; then
    mkdir target
fi
mount $TARGET ./target
# Set the host name
echo ws${number} > ./target/etc/hostname

# Unmount the drive
umount target

