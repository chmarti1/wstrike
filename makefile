BIN=$(HOME)/bin/wstrike
LOG=$(HOME)/wstrike.log


install:
	python3 -m pip install --upgrade pip
	python3 -m pip install pyaudio
	[ -d $(HOME)/bin ] || mkdir $(HOME)/bin
	cp wstrike.py $(BIN)
	chmod 755 $(BIN)
	touch $(LOG)
	chmod 664 $(LOG)
	echo "$(BIN)&" >> $(HOME)/.profile
