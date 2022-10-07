#!/usr/bin/python3
import alsaaudio as aa
import array
import time
import os,psutil,signal,sys

# Needs to run as user wstrike
# $ adduser --system --home /var/local/wstrike --group wstrike
# $ adduser wstrike audio
# $ python3 -m pip install --upgrade pip
# $ python3 -m pip install pyalsaaudio
# Turn off raspberry pi audio somehow?

logfile = '/var/local/wstrike/wstrike.log'
state = {'run':True}
# Set the default parameters
params = {
    'criterion':0,
    'buffer':22050,
    'rate':44100,
    'threshold':512,
    'amplitude':0}
    

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



def halt(s,h):
    state['run'] = False

# Catch a SIGTERM (termination) or SIGINT (keybaord interrupt)
signal.signal(signal.SIGTERM, halt)
#signal.signal(signal.SIGINT, halt)

writelog(logfile, 'START', params={'pid':os.getpid()})

try:
    pcm = aa.PCM(type=aa.PCM_CAPTURE, 
            device='plughw:CARD=Device,DEV=0', 
            channels=1, 
            format=aa.PCM_FORMAT_S16_LE,
            rate=params['rate'],
            periodsize=params['buffer'])

    while state['run']:
        N,v = pcm.read()
        v = array.array('h',v)
        params['amplitude'] = int((max(v) - min(v)) / 2)
        if params['amplitude'] > params['threshold']:
            writelog(logfile, event='STRIKE', params=params)
except:
    e = sys.exc_info()[1]
    writelog(logfile, event='ERROR', params={'message':'"'+repr(e)+'"'})
    writelog(logfile, event='STOP', params={'pid':os.getpid()})
    exit(1)

writelog(logfile, 'STOP', params={'pid':os.getpid()})

