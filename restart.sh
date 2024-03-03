#!/bin/bash



# Systemd xizmatlarini qayta boshlash

git pull
sudo systemctl start djangofather.socket
sudo systemctl enable djangofather.socket
sudo systemctl restart djangofather.socket
sudo systemctl restart djangofather.service
sudo systemctl daemon-reload
sudo nginx -t && sudo systemctl restart nginx