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
Installation creates a `wstrike` user and group.  The `wstrike` servie will 
run as the `wstrike` user, and `wsadmin` runs as `root`.  

The `wstrike` user has a home directory at `/usr/local/wstrike`, where the
system's configuration and log files can be found.  Scripts `wsadmin` and
`wsadmin` are installed in `/usr/local/bin/`, and there are also systemd
service configurations located in `/etc/systemd/system/` named `wstrike.service`
and `wsadmin.service`.  The scripts are plain Python.

The home directory includes a directory called `mnt`, where `wsadmin` will 
automatically mount any devices that appear to be USB keys.  If root of the 
USB key has a directory called `wsadmin`, the service automatically looks 
for `wsadmin/get` and `wsadmin/put`.  See USB communication below for more
information.

## INSTALLING
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
- The python package manager, `pip` is upgraded (requires internet)
- The `pyalsaaudio` package and its dependencies is installed (requires internet)
- The `wstrike` system user is created with a home at `/usr/local/wstrike`
- The home directory is populated with the various log and configuration files
- The `wstrike` and `wsadmin` scripts are placed in `/usr/local/bin`
- The `wstrike.service` and `wsadmin.service` configurations are installed in `/etc/systemd/system/`
- The new services are enabled

To be certain everything has gone as planned, it may be helpful to restart
the system after installation.

## USB Communication

When any USB key is inserted into the Pi, the `wsadmin` service automatically 
inspects it for a directory named `./wsadmin/`.  Inside that directory, two 
special directories are expected: `./wsadmin/get/` and `./wsadmin/put/`.

If `./wsadmin/get` is found, a copy of the following files are copied into
the directory:
- `wstrike.conf` : The configuration file that controls wstrike settings
- `wsadmin.conf` : The configuration file that controls administrative settings
- `wstrike.log` : The primary data file for all strike events
- `wsadmin.log` : A log file for administrative events, update, etc.
- `wstrike.py` : A copy of the current wstrike script in use

Then, if `./wsadmin/put` is found, the oposite is done for any files that are 
found there.  This is available as a mechanism to update or overwrite existing
files on the system without a keyboard or monitor.  If it is found, the `wstrike.py`
file is used to overwrite `/usr/local/bin/wstrike`.  Note that the same option
is NOT available to update `wsadmin`.  

Once a "put" operation is successful, the RPi should automatically restart to
force all changes to take effect.

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

Though this file is required, none of its directives are currently required.  It includes
parameters that are intended for future use - configuring wifi SSID and password
directives and a remote server URL and credentials.  The SSID and password 
functionality is implemented but only lightly tested - it is not currently 
recommended to rely on this for connecting the Pi.