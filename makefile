WSHOME=/var/local/wstrike
WSUSER=wstrike
WSMNT=$(WSHOME)/mnt
BIN=/usr/local/bin/wstrike
ADMBIN=/usr/local/bin/wsadmin
SERVICE=/etc/systemd/system/wstrike.service
ADMSERVICE=/etc/systemd/system/wsadmin.service

install:
	apt install -y libasound2 libasound2-dev
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade pyalsaaudio
	adduser --system --home $(WSHOME) --group $(WSUSER)
	adduser wstrike audio
	# Set up the wstrike home directory
	if [ ! -d $(WSMNT) ]; then mkdir $(WSMNT); fi
	chown root:root $(WSMNT)
	touch $(WSHOME)/wstrike.log
	touch $(WSHOME)/wsadmin.log
	chown $(WSUSER):$(WSUSER) $(WSHOME)/*.log
	chmod 644 $(WSHOME)/*.log
	# Install the binaries
	cp src/wstrike.py $(BIN)
	chmod 755 $(BIN)
	chown root:root $(BIN)
	cp src/wsadmin.py $(ADMBIN)
	chmod 750 $(ADMBIN)
	chown root:root $(BIN)
	# Install configuration files
	cp src/*.conf $(WSHOME)
	chmod 644 $(WSHOME)/*.conf
	chown wstrike:wstrike $(WSHOME)/*.conf
	# Install the services
	cp src/wstrike.service $(SERVICE)
	chown root:root $(SERVICE)
	chmod 644 $(SERVICE)
	systemctl enable wstrike.service
	cp src/wsadmin.service $(ADMSERVICE)
	chown root:root $(ADMSERVICE)
	chmod 644 $(ADMSERVICE)
	systemctl enable wsadmin.service
	# Force UTC timezone
	timedatectl set-timezone UTC

remove:
	systemctl stop wstrike
	systemctl stop wsadmin
	rm $(BIN)
	rm $(ADMBIN)
	rm $(SERVICE)
	rm $(ADMSERVICE)
	rm -rf $(WSHOME)
	deluser wstrike
	systemctl daemon-reload
