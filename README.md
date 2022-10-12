# WSTRIKE

Window strike monitoring service

## ABOUT WSTRIKE
The window strike monitoring utility is designed for installation on a Raspberry Pi.  The system is designed to monitor for bird strikes on a window using a piezo accelerometer fed through a USB audio input.  

Its function is split between two `systemd` services: `wstrike` and `wsadmin`.  `wstrike` is responsible for streaming the audio input and logging events.  `wsadmin` is responsible for communication.


## ABOUT WSTRIKE'S DESIGN
Installation creates a `wstrike` user and group.  The `wstrike` servie will run as the `wstrike` user, and `wsadmin` runs as `root`.  

After install, all of the wstrike system files are copied to the wstrike home directory, `/var/local/wstrike`.  

## INSTALLING
Make sure `python 3.X` is installed.  On a Raspberry pi running Raspbian,
this will be the case by default.

As a normal user (do NOT use sudo) navigate to the wstrike directory and
type the following:
```bash
$ make install
```
This will create a `/home/$USER/bin` directory, and places the `wstrike` 
executable script there.  After restarting the machine, this directory
will automatically be added to the `PATH`, so the `wstrike` command 
will become available to the user.

The installation script also appends a command to start `wstrike` in the
background to the user's `.profile` script, so it will start 
automatically after login.  **Do not run the installation script 
repeatedly** without manually removing this line at the end of 
`$HOME/.profile`.

## ACTIONS 

If it is present, the action verb comes immediately after the `wstrike`
command on the command line.  It tells `wstrike` what the user wants it
to do.

### status 
```bash
$ wstrike status [simple] 
```

Scan all currently running processes to see if wstrike is already 
running. A report is written to stdout.  If the "simple" option is found
only the PID of another wstrike process is printed to the output.


### start 
```bash
$ wstrike start [param:value ...]
```

Calling wstrike with the start action and no options is identical to 
calling wstrike with no options.  Start accepts an indefinite number of
parameter-value pairs separated by colons.  The most important of these
is the criterion option, which selects the algorithm that will be used
to identify a recordable event.

For example, the default settings are equivalent to this command:
```bash
$ wstrike start criterion:0 rate:44100 threshold:512 buffer:22050 &
```
See the criteria section below for more information...


### debug 
```bash
$ wstrike debug [param:value ...]
```
The debug action is identical to the start action, but it does not log
events.  Instead, it prints them to stdout.


### stop 
```bash
$ wstrike stop
```
This action takes no options.  It sends a SIGTERM signal to any running
wstrike processes to halt them gracefully.  When wstrike is halted in 
this way, it logs the stop time in the wstrike.log file.


## CRITERIA 

The criterion parameter may be set to an integer that indicates which
algorithm will be used to detect a potential bird strike event.  
Currently, there is only one criterion. 


### criterion:0 
This is a simple amplitude threshold test.  It recognizes parameters:
- rate        The audio sample rate in Hz
- threshold   The amplitude threshold above which an event is logged
- buffer      The number of samples to collect for each test
    
The threshold amplitude refers to half of the peak-to-peak maximum of 
the signal recorded over the buffer interval.  The data are collected on
a 16-bit scale, so the maximum peak-to-peak amplitude is 65,536, and the
maximum amplitude is 32,768.
