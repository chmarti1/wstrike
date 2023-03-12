# WSADMIN folder

The `wsadmin` folder should be copied to the root directory of any USB
key to be used for communication with the RPi.  Use the `wsadmin/put`
directory to configure the RPi and the `wsadmin/get` directory to 
receive data from the RPi.

To use the USB key, simply place it in one of the USB sockets on the RPi
and wait about fifteen (15) seconds for the window strike administrative
service to move the necessary files.

If you wrote to any important configuration files, you will know the 
changes were successful when the RPi immediately restarts itself.

## Configuring

There are three important configuration files that, if found in 
`wsadmin/put`, will be copied into the system: `wstrike.conf`, 
`wsadmin.conf`, and `wpa_supplicant.conf`.

In addition, if log files are found, they are also used to overwrite the
previous instances of `wstrike.log` and `wsadmin.log`.  This is a 
convenient way to clear old log files, but beware - this permanently 
erases old data.

## WSTRIKE.CONF
```
# WSTRIKE.CONF
#
# The window strike monitoring configuration file is an exectuable 
# python script that defines variables used for configuring the 
# monitoring process.  Each of the options is documented in the comments
# below.

# CRITERION
# The criterion specifies which algorithm will be used to identify a 
# strike event.  Each criterion is identified uniquely by an integer.
# Supported criteria are:
#
# criterion = 0
# Amplitude detection mode.  The input from the audio stream is read at
# certain rate for a duration determined by a buffer size.  Peak-to-peak
# amplitude is the maximum minus the minimum, and a strike is detected
# if the peak is greater than a threshold.
criterion = 0

# RATE
# The sample rate is the number of times the audio signal is sampled 
# every second.  Legal values are: 8000, 16000, 44100, 48000, 96000
rate = 44100

# BUFFER
# The buffer determines the number of audio samples that are accumulated
# before testing for a strike event.  Legal values must be an integer 
# greater than 0 and less than 1,000,000.
#
# The resulting duration between tests is BUFFER / RATE seconds.  For 
# example, if the buffer were 22,050 and the rate were 44,100, then 
# strike events will be logged no more frequently than every 0.5 
# seconds.  The duration may be no shorter than 0.1 seconds, and no 
# longer than 2 seconds.
buffer = 22050

# THRESHOLD
# The threshold is the smallest peak-to-peak amplitude that will be 
# logged as a strike event.  Since the audio stream is sampled as a 
# signed 16-bit integer, the amplitude is on a scale from 0 to 65,535.
# 
# The threshold may be any integer greater than 100 and smaller than 
# 65,000.
threshold = 1024
```

## WSADMIN.CONF

As of version 0.3, all of the directives in the `wsadmin.conf` file are ignored.  These features are reserved for future functionality that will allow `wsadmin` to 
```
#remote_url **SERVER URL HERE**
#remote_user **SERVER USERNAME HERE**
#remote_password **SERVER PASSWORD HERE**
```

## WPA_SUPPLICANT.CONF
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
