#!/usr/bin/python3
import alsaaudio as aa
import array
import time
import os,signal,sys,shutil

# Needs to run as user wstrike
# $ adduser --system --home /var/local/wstrike --group wstrike
# $ adduser wstrike audio
# $ python3 -m pip install --upgrade pip
# $ python3 -m pip install pyalsaaudio
# 

homedir = '/var/local/wstrike'
logfile = os.path.join(homedir, 'wstrike.log')
paramfile = os.path.join(homedir, 'wstrike.conf')
#pcm_device = 'plughw:CARD=Device,DEV=0'
card_name = 'USB Audio Device'
card_mixer_control = 'Mic'
status_every = 3600
version = '0.2'

# Initialize the global state variables
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


# Finally, the script...
if __name__ == '__main__':
    writelog(logfile, 'START', params={'pid':os.getpid(), 'version':version})

    # Catch a SIGTERM (termination) or SIGINT (keybaord interrupt)
    signal.signal(signal.SIGTERM, halt)
    #signal.signal(signal.SIGINT, halt)

    # Load the configuration file
    if os.path.isfile(paramfile):
        try:
            # Make a copy of the default parameters
            temp_params = params.copy()
            with open(paramfile,'r') as ff:
                exec(ff.read(), None, temp_params)
            
            valid_criterion = [0]
            valid_rate = [8000, 16000, 44100, 48000, 96000]
            
            # Check the parameters for illegal content
            for thisparam,thisvalue in temp_params.items():
                # Test the parameters for legal values
                if thisparam == 'criterion':
                    if thisvalue not in valid_criterion:
                        raise Exception(f'In file ({paramfile}) parameter ({thisparam}={thisvalue}) only accepts values: ' + repr(valid_criterion))
                elif thisparam == 'rate':
                    if thisvalue not in valid_rate:
                        raise Exception(f'In file ({paramfile}) parameter ({thisparam}={thisvalue}) only accepts values: ' + repr(valid_rate))
                elif thisparam == 'threshold':
                    if not isinstance(thisvalue, int) or thisvalue < 100 or thisvalue > 65000:
                        raise Exception(f'In file ({paramfile}) paramete ({thisparam}={thisvalue}) only accepts integers between 100 and 65000')
                # We'll deal with the buffer last
                elif thisparam == 'buffer':
                    pass
                # Ignore the amplitude parameter
                elif thisparam == 'amplitude':
                    pass
                else:
                    raise Exception(f'Unrecognized/illegal parameter ({thisparam}) in file: {paramfile}')
            # Finally, all the parameters are loaded, now check the buffer duration
            thisparam = 'buffer'
            thisvalue = temp_params[thisparam]
            duration = thisvalue / temp_params['rate']
            if not isinstance(thisvalue, int) or thisvalue < 0 or thisvalue > 1e6:
                raise Exception(f'In file ({paramfile}) parameter ({thisparam}={thisvalue}) only accepts integers greater than 0 and less than 1 000 000.')
            elif duration < 0.1 or duration > 2:
                raise Exception(f'In file ({paramfile}) the buffer and rate parameters result in a sample duration less than 0.1 seconds or greater than 2 seconds.  Adjust one or both.')

            # OK, update the parameters
            params.update(temp_params)
        except:
            e = sys.exc_info()[1]
            writelog(logfile, event='ERROR', params={'message':'"'+repr(e)+'"'})
            writelog(logfile, event='STOP', params={'pid':os.getpid()})
            exit(-1)


    # Scan for the USB Audio Device
    card_index = -1
    card_name_long = ''
    for ii in aa.card_indexes():
        name = aa.card_name(ii)
        # If the name matches, this is the correct device
        if name[0] == card_name:
            card_index = aa.card_indexes()[ii]
            card_name_long = name[1]
            break
    if card_index < 0:
        writelog(logfile, 'ERROR', params={'message':'Did not find an audio device with name: ' + card_name})
        writelog(logfile, 'STATUS', params={'message':'Attempting to start with default settings - unlikely to succeed!'})
    else:
        writelog(logfile, 'STATUS', params={'message':'Found audio device: ' + card_name_long})

    # Initialize the audio interface through ALSA
    pcm = None
    try:
        pcm = aa.PCM(type=aa.PCM_CAPTURE, 
                cardindex=card_index,
                channels=1,
                format=aa.PCM_FORMAT_S16_LE,
                rate=params['rate'],
                periodsize=params['buffer'])
        failed = False
    except:
        writelog(logfile, 'ERROR', params={'message':'Failed to initialize audio.'})
        writelog(logfile, 'STOP', params={'pid':os.getpid()})
        exit(-1)

        
    # Set the capture volume to maximum
    try:
        # Set the volume to max
        m = aa.Mixer(control=card_mixer_control, cardindex=card_index)
        m.setvolume(100)
    except:
        writelog(logfile, 'ERROR', params={'message':'Failed to set the audio capture volume.'})
        

    try:
        while state['run']:
            N,v = pcm.read()
            v = array.array('h',v)
            params['amplitude'] = int((max(v) - min(v)))
            if params['amplitude'] > params['threshold']:
                writelog(logfile, event='STRIKE', params=params)
    except:
        e = sys.exc_info()[1]
        writelog(logfile, event='ERROR', params={'message':'"'+repr(e)+'"'})
        writelog(logfile, event='STOP', params={'pid':os.getpid()})
        exit(1)

    writelog(logfile, 'STOP', params={'pid':os.getpid()})

