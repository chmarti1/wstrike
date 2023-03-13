# WSTRIKE  

Window strike monitoring service

## ABOUT WSTRIKE  
The window strike monitoring utility is designed for installation on a 
Raspberry Pi.  The system is designed to monitor for bird strikes on a 
window using a piezo accelerometer fed through a USB audio input.  

Its function is split between two `systemd` services: `wstrike` and `wsadmin`.  
`wstrike` is responsible for streaming the audio input and logging events.  
`wsadmin` is responsible for configuration and communication of data.

## ABOUT WSTRIKE'S DESIGN  

Installation with 
```bash
$ sudo make install
```
creates a `wstrike` user and group.  The `wstrike` servie will 
run as the `wstrike` user, and `wsadmin` runs as `root`.  

The `wstrike` user has a home directory at `/usr/local/wstrike`, where the
system's configuration and log files can be found.  Executable plain Python
scripts `wstrike` and `wsadmin` are installed in `/usr/local/bin/`, and 
there are also systemd service configurations located in 
`/etc/systemd/system/` named `wstrike.service` and `wsadmin.service`.

The home directory includes a directory called `mnt`, where `wsadmin` will 
automatically mount any devices that appear to be USB keys.  If root of the 
USB key has a directory called `wsadmin`, the service automatically looks 
for `wsadmin/get` and `wsadmin/put`.  See USB communication below for more
information.

## Installing from makefile  

Make sure `python 3.X` is installed.  On a Raspberry pi running Raspbian,
this will be the case by default.

First, make sure the Rapberry Pi has a working internet connection.  The 
installation script will automatically install certain dependencies to make
sure your wstrike installation has everything it needs to work.

Open a terminal (Ctrl+t or Accessories->Terminal in the RPi menu).  Download
the latest distribution of 
```bash
$ git clone https://github.com/chmarti1/wstrike
  ...
$ cd wstrike
```
This should download the latest distribution of the wstrike package.  Now, 
it's time to install the package. 
```bash
$ sudo make install
```
The `sudo` before the `make install` command executes this an administrator.
By default the `pi` user should be allowed to run this command in RaspbianOS.

This performs a number of steps:  
- Apt installs libasound2 and its headers (requires internet)
- The python package manager, `pip` is upgraded (requires internet)
- The `pyalsaaudio` package and its dependencies is installed (requires internet)
- The `wstrike` system user is created with a home at `/usr/local/wstrike`
- The home directory is populated with the various log and configuration files
- The `wstrike` and `wsadmin` scripts are placed in `/usr/local/bin`
- The `wstrike.service` and `wsadmin.service` configurations are installed in `/etc/systemd/system/`
- The new services are enabled 

Once installation is successful, cycle power to the device or force a restart.
The services should start automatically durring boot, and their status should be
available by checking their log files:
```bash
$ cat /var/local/wstrike/wstrike.log
  ...
$ cat /var/local/wstrike/wsadmin.log
  ...
```

## Installing from image  

For mass distribution, it is better to copy an image of an SD card with a working
installation already done.  That can be done in Windows or Linux using the `dd`
utility.  Documenting that procedure is for a different readme.

## USB Communication  

Once installation is successful, the `wsadmin` service automatically 
inspects it for a directory named `./wsadmin/`.  Inside that directory, two 
special directories are expected: `./wsadmin/get/` and `./wsadmin/put/`.

If `./wsadmin/get` is found, a copy of the following files are copied into
the directory:
- `wstrike.conf` : The configuration file that controls wstrike settings
- `wsadmin.conf` : The configuration file that controls administrative settings
- `wstrike.log` : The primary data file for all strike events
- `wsadmin.log` : A log file for administrative events, update, etc.
- `wstrike.py` : A copy of the current wstrike script in use
- `wpa_supplicant.conf` : A copy of the system's wifi configuration file

Then, if `./wsadmin/put` is found, the oposite is done for any files that are 
found there.  This is available as a mechanism to update or overwrite existing
files on the system without a keyboard or monitor.  If it is found, the `wstrike.py`
file is used to overwrite `/usr/local/bin/wstrike`.  Note that the same option
is NOT available to update `wsadmin`.  

Once a "put" operation is successful, the RPi should automatically restart to
force all changes to take effect.  Note that the status LEDs don't necessarily
turn off when that happens.

See also the `./wsadmin/README.md` for more information.

## WSTRIKE.CONF  

The configuration files are plain Python code that is used to define parameters 
that are expected by their executables.  `wstrike.conf` is used to define the 
criteria for a strike event.

The ALSA audio system is configured through the `pyalsaaudio` package to stream 
audio data, and it is continuously checked for strong signals from the sensor.  
If there is a strong signal, it is logged as a STRIKE event along with a timestamp.

The `wstrike.conf` file that installs by default is heavily commented to explain the
meaning of the various parameters.

## WSADMIN.CONF  

Though this file is required, none of its directives are currently used.  These
parameters that are intended for future use with remote server connections.  

## WPA_SUPPLICANT.CONF  

The `wpa_supplicant.conf` file is used to configure the wifi connection.
This is not a part of the WSTRIKE system - instead it is a normal part
of the Linux network configuration system.  A typical file might appear:
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
	ssid="YOUR_WIFI_NETWORK_ID_HERE"
	psk="YOUR_WIFI_PASSWORD_HERE"
	key_mgmt=WPA-PSK
}
```

You should edit the ssid and psk entries as necessary to allow the pi to
connect to your wifi network.  Make sure to leave the quotation marks.
For more information, see [the Raspberry Pi documentaiton](https://www.raspberrypi.com/documentation/computers/configuration.html#using-the-command-line),
or the [Linux man pages](https://linux.die.net/man/5/wpa_supplicant.conf).
A more detailed documentation is available (here)[https://man.freebsd.org/cgi/man.cgi?wpa_supplicant.conf(5)].
