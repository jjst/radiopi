#!/bin/sh

sudo pip3 install -r requirements.txt
echo "Setting up radiopi as systemd service..."
sudo ln -sf $PWD/radio.py /usr/bin/radiopi
sudo cp ./install/systemd/radiopi.service /etc/systemd/system/radiopi.service
sudo chmod 644 /etc/systemd/system/radiopi.service
sudo systemctl enable radiopi
echo "Install successful."
