WSHOME=/var/local/wstrike
WSUSER=wstrike
BIN=/usr/local/bin/wstrike
LOG=$(WSHOME)/wstrike.log
SERVICE=/etc/systemd/system/wstrike.service

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade pyalsaaudio
	adduser --system --home $(WSHOME) --group $(WSUSER)
	adduser wstrike audio
	cp wstrike.py $(BIN)
	chmod 755 $(BIN)
	chown root:root $(BIN)
	touch $(LOG)
	chown $(WSUSER):$(WSUSER) $(LOG)
	chmod 664 $(LOG)
	cp wstrike.service $(SERVICE)
	chown root:root $(SERVICE)
	chmod 644 $(SERVICE)
remove:
	deluser --remove-home wstrike
	rm $(BIN)
	rm $(SERVICE)
	
