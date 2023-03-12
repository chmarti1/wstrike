v0.2 12/1/2022
First assigned version number.  
- Added Version number in the START log notification
- Changed systemd startup behavior to restart every 5s
TODO: Still need to add automatic time server updates

v0.3 3/12/2023  
- Added wpa_supplicant.conf to the put/get files for wifi support  
- Tested the native time server updates  
- Added excessive log filter to wstrike.py  
- Installation now sets system timezone to UTC
- Both logs now log the system host name
- The host name is now set at installation (/etc/hostname, /etc/hosts)
