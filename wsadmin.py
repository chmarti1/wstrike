#!/usr/bin/python3

import os,shutil,signal,sys
import time


state = {'run':True}
params = {
    'wifi_ssid':None, 
    'wifi_key':None,
    'remote_url':None,
    'remote_user':None,
    'remote_password':None
    }
interval = 10
wshome = '/var/local/wstrike'
wsuser = 'wstrike'
logfile = os.path.join(wshome, 'wsadmin.log')
configfile = os.path.join(wshome, 'wsadmin.conf')
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
        # Schedule a list of files to transfer
        schedule = [
            [os.path.join(wshome, 'wstrike.conf'), os.path.join(get, 'wstrike.conf')],
            [os.path.join(wshome, 'wstrike.log'), os.path.join(get, 'wstrike.log')],
            ['/usr/local/bin/wstrike', os.path.join(get, 'wstrike.py')],
            [configfile, os.path.join(get, 'wsadmin.conf')],
            [logfile, os.path.join(get, 'wsadmin.log')]]
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
                # Reload the configuration and update the supplicant file
                config()
                wifi()
        except:
            e = sys.exc_info()[1]
            writelog(logfile, 'ERROR durring PUT: '+repr(e))
    # Unmount the usb drive
    if mounted:
        os.system(f'umount {mnt}')
        
    if restart:
        os.system('shutdown -r now')

    
def wifi():
    try:
        writelog(logfile, 'Updating wpa_supplicant for ssid: ' + params['wifi_ssid'])
        source = '/etc/wpa_supplicant/wpa_supplicant.conf'
        target = '/etc/wpa_supplicant/wpa_supplicant._conf'
        # We'll make a new configuration file and overwrite the old
        # as the last step
        with open(target, 'w') as tf:
            with open(source, 'r') as sf:
                # Copy up to the first network definition
                for thisline in sf:
                    if thisline.startswith('network'):
                        break
                    tf.write(thisline)
            # We're done with the source file, so close it
            tf.write(f'network={{\n\tssid="{params["wifi_ssid"]}"\n\tpsk="{params["wifi_key"]}"\n\tkey_mgmt=WPA-PSK\n}}\n')
        # Finally, overwrite the old
        shutil.move(target, source)
        
    except:
        e = sys.exc_info()[1]
        writelog(logfile, f'ERROR updating wpa_supplicant: ' + repr(e))

    

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, halt)
    # Log the service coming online
    writelog(logfile, f'START pid={os.getpid()}')
    config()
    wifi()
    
    # Service loop
    while state['run']:
        # Check for USB partitions
        source = '/dev/disk/by-path'
        drives = os.listdir('/dev/disk/by-path')
        # Limit the list to USB devices that have a partition number
        for d in drives:
            # If this appears to be a USB drive partition
            if 'usb' in d and 'part' in d:
                sync(os.path.join(source, d))
                
        
        # Go to sleep for a while
        time.sleep(interval)
    # Log the service going offline
    writelog(logfile, f'STOP pid={os.getpid()}')
