#!/bin/sh

sudo ln -sf ./radio.py /usr/bin/radiopi
sudo cp ./install/systemd/radiopi.service /etc/systemd/system/radiopi.service
sudo chmod 644 /etc/systemd/system/radiopi.service
sudo systemctl enable radiopi
