#!/usr/bin/python3

import os,shutil,signal,sys
import time


state = {'run':True}
params = {
    'remote_url':None,
    'remote_user':None,
    'remote_password':None
    }
interval = 10                           # Run the wsadmin services every 10 seconds
inet_interval = 24*3600 / interval      # Check the network every 24 hours
wshome = '/var/local/wstrike'           
wsuser = 'wstrike'
logfile = os.path.join(wshome, 'wsadmin.log')
configfile = os.path.join(wshome, 'wsadmin.conf')
wpaconfig = '/etc/wpa_supplicant/wpa_supplicant.conf'
mnt = os.path.join(wshome, 'mnt')


def writelog(logfile, event):
    """writelog(logfile, event)
Write to the wstrike log file /var/log/wstrike.log

Each entry takes the format:
[TIMESTAMP] EVENT
"""
    now = time.strftime('%Y-%m-%d %H:%M:%S,UTC%z')
    logline = f'[{now}] {event}\n'
    
    if isinstance(logfile, str):
        with open(logfile, 'a') as fd:
            fd.write(logline)
    else:
        logfile.write(logline)


def halt(s,h):
    state['run'] = False
    
def config():
    # Read the configuration file
    try:
        ii = -1
        with open(configfile, 'r') as ff:
            for ii, thisline in enumerate(ff):
                thisline = thisline.strip()
                if len(thisline)>0 and not thisline.startswith('#'):
                    param, value = thisline.split()
                    if param not in params:
                        raise Exception('Unrecognized parameter: ' + param)
                    params[param] = value
    except:
        e = sys.exc_info()[1]
        writelog(logfile, f'ERROR parsing line {ii} in configuration file: '+ configfile)
        writelog(logfile, repr(e))
    
def testinet():
    try:
        cmd = 'ping -c 1 -W 2 ipinfo.io'
        err = os.system(cmd)
        if err:
            writelog(logfile, f'STATUS Ping failure ({err}): ' + cmd)
        else:
            writelog(logfile, f'STATUS Ping success: ' + cmd)
    except:
        e = sys.exc_info()[1]
        writelog(logfile, f'ERROR testing internet connection.')
        writelog(logfile, repr(e))
    
    
    
def sync(drive):
    # Clear a flag indicating whether to restart the machine
    restart = False
    
    # Try to mount the drive
    mounted = not os.system(f'mount {drive} {mnt}')
    if not mounted:
        writelog(logfile, f'ERROR Failed: mount {drive} {mnt}')
        
    put = os.path.join(mnt, 'wsadmin', 'put')
    get = os.path.join(mnt, 'wsadmin', 'get')
    # Check for a wsadmin/get directory
    if os.path.isdir(get):
        # Log the transfer
        writelog(logfile, 'STATUS Transferring to USB wsadmin/get')
        # Schedule a list of files to transfer
        schedule = [
            [os.path.join(wshome, 'wstrike.conf'), os.path.join(get, 'wstrike.conf')],
            [os.path.join(wshome, 'wstrike.log'), os.path.join(get, 'wstrike.log')],
            ['/usr/local/bin/wstrike', os.path.join(get, 'wstrike.py')],
            [configfile, os.path.join(get, 'wsadmin.conf')],
            [logfile, os.path.join(get, 'wsadmin.log')],
            [wpaconfig, os.path.join(get, 'wpa_supplicant.conf')]]
        for source,target in schedule:
            try:
                shutil.copy(source,target)
            except:
                e = sys.exc_info()[1]
                writelog(logfile, f'ERROR copying {source} to {target}')
                writelog(logfile, 'ERROR durring GET: '+repr(e))
    
    # Check for a wsadmin/put directory
    if os.path.isdir(put):
        try:
            # Work through the possible files one-by-one
            contents = os.listdir(put)
            if 'wstrike.conf' in contents:
                source = os.path.join(put,'wstrike.conf')
                target = os.path.join(wshome, 'wstrike.conf')
                writelog(logfile, f'Moving {source} to {target}')
                if os.system(f'mv {source} {target};chown {wsuser}:{wsuser} {target};chmod 664 {target}'):
                    writelog(logfile, 'ERROR Operation failed')
                restart = True
            if 'wstrike.log' in contents:
                source = os.path.join(put,'wstrike.conf')
                target = os.path.join(wshome, 'wstrike.conf')
                writelog(logfile, f'Moving {source} to {target}')
                if os.system(f'mv {source} {target};chown {wsuser}:{wsuser} {target};chmod 644 {target}'):
                    writelog(logfile, 'ERROR Operation failed')
            if 'wstrike.py' in contents:
                source = os.path.join(put, 'wstrike.py')
                target = '/usr/local/bin/wstrike'
                writelog(logfile, f'Moving {source} to {target}')
                if os.system(f'mv {source} {target};chown {root}:{root} {target};chmod 755 {target}'):
                    writelog(logfile, 'ERROR Operation failed')
                restart = True
            if 'wsadmin.log' in contents:
                source = os.path.join(put, 'wsadmin.log')
                target = logfile
                writelog(logfile, f'Moving {source} to {target}')
                if os.system(f'mv {source} {target};chown {wsuser}:{wsuser} {target};chmod 644 {target}'):
                    writelog(logfile, 'ERROR Operation failed')
            if 'wsadmin.conf' in contents:
                source = os.path.join(put, 'wsadmin.conf')
                target = configfile
                writelog(logfile, f'Moving {source} to {target}')
                if os.system(f'mv {source} {target};chown {wsuser}:{wsuser} {target};chmod 660 {target}'):
                    writelog(logfile, 'ERROR Operation failed')
                restart = True
            if 'wpa_supplicant.conf' in contents:
                source = os.path.join(put, 'wpa_supplicant.conf')
                target = wpaconfig
                writelog(logfile, f'Moving {source} to {target}')
                if os.system(f'mv {source} {target};chown root:root {target};chmod 600 {target}'):
                    writelog(logfile, 'ERROR Operation failed')
                restart = True
        except:
            e = sys.exc_info()[1]
            writelog(logfile, 'ERROR durring PUT: '+repr(e))
    # Unmount the usb drive
    if mounted:
        os.system(f'umount {mnt}')
        
    if restart:
        os.system('shutdown -r now')

    

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, halt)
    # Log the service coming online
    writelog(logfile, f'START pid={os.getpid()} device={os.uname()[1]}')
    config()
    
    # A synclock will prevent repeated synchronizations if a USB key is left in
    synclock = False
    # This counter will keep track of when it's time to test the network
    inet_counter = 6
    
    # Service loop
    while state['run']:
        # Check for USB partitions
        source = '/dev/disk/by-path'
        drives = os.listdir(source)
        # Limit the list to USB devices that have a partition number
        found_usb = False
        for d in drives:
            # If this appears to be a USB drive partition
            # Do not check for 'part' anymore - causes problems with non-partitioned USB drives
            # Tested on drives with partitions - still seems to work without problems
            #if 'usb' in d and 'part' in d:
            if 'usb' in d:
                # Mark that we found a USB drive
                found_usb = True
                # If the synclock is free, perform the sync
                if not synclock:
                    sync(os.path.join(source, d))
        # Maintain the synclock as long as there is a usb present
        synclock = found_usb
        
        # Check the internet connection
        if inet_counter <= 0:
            inet_counter = inet_interval
            testinet()
        # Decrement the counter
        inet_counter -= 1
        
        # Go to sleep for a while
        time.sleep(interval)
    # Log the service going offline
    writelog(logfile, f'STOP pid={os.getpid()}')
