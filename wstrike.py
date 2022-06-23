#!/usr/bin/python3

# WSTRIKE
# Window strike monitor

import pyaudio as pa
import array
import time
import os,psutil,signal,sys

# Set the default parameters
params = {
    'criterion':0,
    'buffer':22050,
    'rate':44100,
    'threshold':512}


def writelog(logfile, event, params={}):
    """writelog(logfile, event, params={})
Write to the wstrike log file /var/log/wstrike.log

Each entry takes the format:
[TIMESTAMP] EVENTTYPE PARAM:VALUE ...

The timestamp and eventtype are mandatory, and all following parameter
value pairs are event dependent and separated by white space.

If logfile is a string, it is treated as a path to a file to which the
event should be appended.  Otherwise, logfile is treated as an output
stream with a write() method.
"""
    now = time.strftime('%Y-%m-%d %H:%M:%S,UTC%z')
    logline = f'[{now}] {event}'
    for key,value in params.items():
        logline += f' {key}:{value}'
    logline += '\n'
    
    if isinstance(logfile, str):
        with open(logfile, 'a') as fd:
            fd.write(logline)
    else:
        logfile.write(logline)


def getproc(lockfile):
    """Retrieve a psutil process instance for the running wstrike
If wstrike is not found to be running, returns None instead.
"""
    if os.path.isfile(lockfile):
        try:
            with open(lockfile, 'r') as fd:
                pid = int(fd.read())
        except:
            print('WARNING: Failed to read lockfile: ' + lockfile)
            print(' attempting removal!')
            os.remove(lockfile)
            return None
        # Recover the process and verify that it is wstrike
        if psutil.pid_exists(pid):
            for proc in psutil.process_iter():
                if proc.pid == pid:
                    if proc.name() != 'wstrike':
                        print('WARNING: Found a lock file for process id: ' + str(pid))
                        print('  Found a different process with that PID: ' + proc.name())
                    return proc
            raise Exception('PANIC! psuitl is giving contradictory information about process id: ' + str(pid))
        # The lockfile exists, but the PID isn't there.
        print('WARNING: The lock file appears to be out of date: ' + lockfile)
        print('  attempting removal!')
        os.remove(lockfile)
            
    return None
            


def criterion0(params):
    signal = array.array('h', astream.read(params['buffer']))
    params['amplitude'] = int((max(signal) - min(signal)) / 2)
    

helptext = """Window strike monitoring utility
    wstrike [ACTION [OPTIONS...]]
    
** ABOUT WSTRIKE **
The window strike monitoring utility monitors for bird strikes on a 
window using a piezo accelerometer fed through an audio input.  When run
normally, with no options, wstrike runs silently until a strike event
occurs, when it logs an event in the wstrike.log file.

$ wstrike &

Adding the & at the end of the command causes it to fork off and run in
the background without blocking the terminal.

For any other than the default behavior, wstrike can be called with an 
action and a series of options.  See the ACTIONS section below.


** ABOUT WSTRIKE'S DESIGN **
For many reasons, it would make sense for this to be a daemon registered
with systemd, running quietly in the background automatically on boot.
However, the easiest way to gain access to the sound stream for sensor
input is to run in user space.  As a result, for the time being, this
is merely an executable script that lives in $HOME/bin, and is 
automatically executed by $HOME/.profile when the user logs in.


** ACTIONS **

If it is present, the action verb comes immediately after the `wstrike`
command on the command line.  It tells `wstrike` what the user wants it
to do.

-- status --
$ wstrike status [simple]

Scan all currently running processes to see if wstrike is already 
running. A report is written to stdout.  If the "simple" option is found
only the PID of another wstrike process is printed to the output.


-- start --
$ wstrike start [param:value ...]

Calling wstrike with the start action and no options is identical to 
calling wstrike with no options.  Start accepts an indefinite number of
parameter-value pairs separated by colons.  The most important of these
is the criterion option, which selects the algorithm that will be used
to identify a recordable event.

For example, the default settings are equivalent to this command:

$ wstrike start criterion:0 rate:44100 threshold:512 buffer:22050 &

See the criteria section below for more information...


-- debug --
$ wstrike debug [param:value ...]

The debug action is identical to the start action, but it does not log
events.  Instead, it prints them to stdout.


-- stop --
$ wstrike stop

This action takes no options.  It sends a SIGTERM signal to any running
wstrike processes to halt them gracefully.  When wstrike is halted in 
this way, it logs the stop time in the wstrike.log file.


** CRITERIA **
The criterion parameter may be set to an integer that indicates which
algorithm will be used to detect a potential bird strike event.  
Currently, there is only one criterion. 


-- criterion:0 --
This is a simple amplitude threshold test.  It recognizes parameters:
    rate        The audio sample rate in Hz
    threshold   The amplitude threshold above which an event is logged
    buffer      The number of samples to collect for each test
    
The threshold amplitude refers to half of the peak-to-peak maximum of 
the signal recorded over the buffer interval.  The data are collected on
a 16-bit scale, so the maximum peak-to-peak amplitude is 65,536, and the
maximum amplitude is 32,768.
"""


# Do not execute if this file was imported instead of executed
if __name__ == '__main__':

    # initialize the user argument state machine
    action = 'start'
    options = []

    # Set the default logfile
    logfile = os.path.expanduser('~/wstrike.log')
    # The location of a lockfile
    lockfile = os.path.expanduser('~/.wstrike.lock')
    
    
    # Process command line options
    if len(sys.argv) > 2:
        action = sys.argv[1]
        options = sys.argv[2:]
    elif len(sys.argv) > 1:
        action = sys.argv[1]
    
    # process the actions
    if action == 'help':
        print(helptext)
        exit(0)
    elif action=='stop':
        # Check for an existing process called wstrike
        # First, check our PID
        mypid = os.getpid()
        proc = getproc(lockfile)
        if proc is not None and 'wstrike' == proc.name() and proc.pid != mypid:
            print('Sending SIGTERM to wstrike:' + repr(proc.pid))
            proc.terminate()
            # wait for all terminated processes to be done
            term,alive = psutil.wait_procs([proc], timeout=3, callback=lambda proc: print('Process terminated normally:' + repr(proc.pid)))
            for proc in alive:
                print('Process is not responding, killing:' + repr(proc.pid))
                proc.kill()
        exit(0)
        
    elif action == 'status':
        simple = False
        for opt in options:
            if opt == 'simple':
                simple = True
            else:
                raise Exception('Unrecognized option for STATUS mode: ' + opt)
        
        # Check for an existing process called wstrike
        # First, check our PID
        mypid = os.getpid()
        proc = getproc(lockfile)
        if proc is None:
            if not simple:
                print('This PID: ' + str(mypid))
                print('STOPPED.')
        else:
            if simple:
                print(str(proc.pid))
            else:
                print('This PID: ' + str(mypid))
                print('RUNNING ' + proc.name() + ': ' + str(proc.pid))
            
        exit(0)
    elif action == 'debug':
        logfile = sys.stdout
    elif action == 'start':
        pass
    else:
        raise Exception('Unrecognized wstrike action: ' + action)
        

    # Test for a process already running
    # If the lockfile was already created, open it and check to verify
    # that the PID is real
    proc = getproc(lockfile)
    if proc is None:
        with open(lockfile,'x') as fd:
            fd.write(str(os.getpid()))
    else:
        raise Exception('A wstrike process already appears to be running: ' + str(proc.pid))
    
    # Process the options
    for opt in options:
        # Raise an error if the parameter does not already exist and if
        # its value cannot be converted to match the current type
        param,value = opt.split(':')
        cvalue = params.get(param)
        if cvalue is None:
            raise Exception('Unrecognized optional parameter: ' + param)
        try:
            params[param] = type(cvalue)(value)
        except:
            raise Exception('Illegal value: ' + repr(value) + ' for parameter: ' + param)
    
    # Always set the capture volume to 100%
    # Use the command line's alsamixer utility
    err = os.system('amixer set Capture 100%')
    if err:
        writelog(logfile, event='ERROR', params={'number':err, 'message':'"Failed to initialize ALSA volume."'})

    writelog(logfile, event='START', params={'pid':os.getpid()})

    p = pa.PyAudio()
    astream = p.open(format=pa.paInt16, channels=1, rate=params['rate'], input=True)

    state = {'run':True}

    def halt(s,h):
        writelog(logfile, event='STOP', params={'pid':os.getpid()})
        os.remove(lockfile)
        state['run'] = False
        
    # Catch a SIGTERM (termination) or SIGINT (keybaord interrupt)
    signal.signal(signal.SIGTERM, halt)
    #signal.signal(signal.SIGINT, halt)
    
    try:
        while state['run']:
            v = array.array('h', astream.read(params['buffer']))
            params['amplitude'] = int((max(v) - min(v)) / 2)
            if params['amplitude'] > params['threshold']:
                writelog(logfile, event='STRIKE', params=params)
    except:
        e = sys.exc_info()[1]
        writelog(logfile, event='ERROR', params={'message':'"'+repr(e)+'"'})
        halt(None, None)
        exit(1)
    exit(0)
