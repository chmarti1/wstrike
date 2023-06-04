# WSTRIKE DISTRIBUTION UTILITY

The `putimg.sh` bash script accepts three command line arguments
```
$ ./putimg.sh <source.img> <target.dev> <number>
```

The `<source>` is the image to copy.  Usually, it will be `ws0.img`.

The `<target.dev>` is the device (drive) to write to.  On some systems, this will be `/dev/mmcblk0` or it might be `/dev/sda`.  This will be the system file representing the device being written.  *NOTE* that this should be the root device and NOT a device partition, like `/dev/mmcblk0p1` or `/dev/sda1`.

The `<number>` will be used to construct the device's system name, `ws<number>`.  For example, if called with `15` as the last argument, the system name of the installation created will be `ws15`.

The utility may raise warnings like `umount: /dev/mmcblk0: not mounted.`  The first step of writing to the drive is to force unmount it and all its partitions so no other system utility can be disrupted while it is using the device.  If the device is not already mounted, this is fine.

