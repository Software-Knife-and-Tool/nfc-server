#
# nfc-env development
#
.PHONY: install nfc app ufw

BASE = /home/putnamjm/ndef-server
PACKAGES = $(BASE)/modules:$(BASE)/../.local/lib/python3.9/site-packages

install:
	@sudo apt install -y python3-pip
	@pip3 install bottle jyserver nfcpy
	@sudo make -C ./service install
	@echo make sure you add `hostname` to the hosts file

ufw:
	@sudo apt install -y ufw
	@sudo ufw allow ssh
	@sudo ufw allow 8080
	@sudo ufw allow 443
	@sudo ufw enable
	@sudo ufw status	

nfc-tool:
	@sudo env "PYTHONPATH=$(PACKAGES)" python3 $(BASE)/nfc-tool.py

server:
	@env "PYTHONPATH=$(PACKAGES)" python3 $(BASE)/app.py
