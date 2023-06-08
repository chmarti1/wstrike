# WSTRIKE DISTRIBUTION UTILITY

The `putimg.sh` bash script accepts three command line arguments
```
putimg.sh <source> <target.dev> <number>
```
For example, the following writes an image found at `~/ws0.img` to the `/dev/mmcblk0` storage device with the name `ws2`.
```
$ sudo ./putimg.sh ~/ws0.img /dev/mmcblk0 2
[sudo] password for chris:         
Write file /home/chris/ws0.img to device /dev/mmcblk0 with name ws2.
Are you sure? (y/n):y
umount: /dev/mmcblk0: not mounted.
```

The `sudo` before the `putimg.sh` command forces the script to run as a priviledged user.  You will need those permissions to mount the device and perform the byte-wise write operation.

The `<source>` is the image to copy.  Usually, it will be a path to find `ws0.img` somewhere on the local filesystem.

The `<target.dev>` is the device (drive) to write to.  On some systems, this will be `/dev/mmcblk0` or it might be `/dev/sda`.  This will be the system file representing the device being written.  *NOTE* that this should be the root device and NOT a device partition, like `/dev/mmcblk0p1` or `/dev/sda1`.

The `<number>` will be used to construct the device's system name, `ws<number>`.  For example, if called with `15` as the last argument, the system name of the installation created will be `ws15`.

The utility may raise warnings like `umount: /dev/mmcblk0: not mounted.`  The first step of writing to the drive is to force unmount it and all its partitions so no other system utility can be disrupted while it is using the device.  If the device is not already mounted, this is fine.

## Identifying the drive

In Linux, Physical storage devices (like SD card readers) will show up somewhere in the `/dev` directory, but where depends on which version of Linux you are running.  There are lots of ways to figure it out; here's one:

Step 1: Before you plug in your SD card, type the command
```
$ lsblk
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
nvme0n1     259:0    0 119.2G  0 disk 
├─nvme0n1p1 259:1    0    94M  0 part /boot/efi
├─nvme0n1p2 259:2    0   7.5G  0 part [SWAP]
└─nvme0n1p3 259:3    0 111.7G  0 part /
```

This lists all bulk storage devices, their partitions, and where (if anywhere) they are mounted in the filesystem.  You will see something different - this is just what I happen to have on my laptop.

Step 2: Insert your SD card reader.  Good.

Step 3: Repeat the `lsblk` command.
```
$ lsblk
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda           8:0    0 149.1G  0 disk 
├─sda1        8:1    0   256M  0 part /media/chris/bootfs
└─sda2        8:2    0  29.5G  0 part /media/chris/rootfs
nvme0n1     259:0    0 119.2G  0 disk 
├─nvme0n1p1 259:1    0    94M  0 part /boot/efi
├─nvme0n1p2 259:2    0   7.5G  0 part [SWAP]
└─nvme0n1p3 259:3    0 111.7G  0 part /
```
Again, you may see something different, but the change will not be subtle.  There will be a whole new device tree that will have appeared.  In my case, it was called `sda`.  That means my device is found at `/dev/sda`.

## Writing from a zipped image

The `putimg.sh` script automatically detects if the file is named `*.gz`, and unzips it as it writes to the SD card.  This is pretty good, but it can slow things down.
```
$ sudo ./putimg.sh ws0.img.gz /dev/sda 47
```
This method requires the file to be unzipped as it is written, and the computational work unzipping the file is lost after the write operation is done.

If you're only writing one SD card, this is the right way to do it.  If you're going to write to a few dozen, you may want to unzip the image first.
```
$ gunzip ws0.img.gz
```
After a few minutes, this will have changed `ws0.img.gz` into `ws0.img`.  The file will be 32GB, so make sure you have the space.  Then, you can use the command
```
$ sudo ./putimg.sh ws0.img /dev/sda 47
```
Note that there's no ".gz" behind the ".img" now.  This will be faster because the decompression has already been done.
