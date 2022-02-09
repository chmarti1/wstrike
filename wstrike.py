#!/usr/bin/python3

# WSTRIKE
# Window strike monitor

import pyaudio as pa
import array
import time

BUFFER = 22050
RATE = 44100
THRESHOLD = 512

logfile = '/var/log/wstrike.log'

p = pa.PyAudio()
astream = p.open(format=pa.paInt16, channels=1, rate=RATE, input=True)

while True:
    signal = array.array('h', astream.read(BUFFER))
    amplitude = (max(signal) - min(signal)) / 2
    print(amplitude)
    if amplitude > THRESHOLD:
        with open(logfile, 'a') as fd:
            now = time.strftime('[%Y-%m-%d %H:%M:%S,UTC%z]\n')
            print(now, end='')
            fd.write(now)
        
