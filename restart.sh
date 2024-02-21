#!/bin/bash



# Systemd xizmatlarini qayta boshlash


sudo systemctl start bots.socket
sudo systemctl enable bots.socket
sudo systemctl restart bots.socket
sudo systemctl restart bots.service
sudo systemctl daemon-reload
sudo nginx -t && sudo systemctl restart nginx