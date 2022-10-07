#!/usr/bin/python3
import os,psutil,signal,sys
import time


logfile = '/var/local/wstrike/wstrike.log'
state = {'run':True}


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
    writelog(logfile, event='STOP', params={'pid':os.getpid()})
    state['run'] = False
    exit(0)

# Catch a SIGTERM (termination) or SIGINT (keybaord interrupt)
signal.signal(signal.SIGTERM, halt)


writelog(logfile, 'START')
while state['run']:
    time.sleep(10)
    writelog(logfile, 'wake')
    
writelog('STOP')
