#!/bin/bash



# Systemd xizmatlarini qayta boshlash
sudo systemctl daemon-reload

sudo systemctl restart bots.socket
sudo systemctl restart bots.service

sudo nginx -t && sudo systemctl restart nginx