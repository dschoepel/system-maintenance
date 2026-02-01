# System Maintenance Installer

This document explains how to install the System Maintenance tooling on any Ubuntu server running Webmin.

---

## 1. Create the secure token file

The installer requires a GitHub fine‑grained token with read access to the repository.

Run:

sudo mkdir -p /etc/system-maintenance

sudo chmod 700 /etc/system-maintenance

echo "GITHUB_TOKEN=github_pat_xxxxxxxxxxxxx" | sudo tee /etc/system-maintenance/env > /dev/null

sudo chmod 600 /etc/system-maintenance/env

---

## 2. Run the bootstrap installer

curl -fsSL https://raw.githubusercontent.com/dschoepel/system-maintenance/main/bootstrap.sh | sudo bash


- Ensure git is installed
- Clone or update the repository
- Install the Webmin module
- Install systemd services and timers
- Install journald configuration
- Install the maintenance script

---

## 3. Verify installation

Check the Webmin module:

Webmin → System Maintenance

Check the systemd service:

sudo systemctl status system-maintenance.service

Check the timer:

sudo systemctl list-timers | grep system-maintenance

---

## 4. Updating the system

To update to the latest version:

cd /opt/system-maintenance-repo

sudo git pull

sudo bash install.sh

---

## 5. Updating the GitHub token

Edit:

sudo nano /etc/system-maintenance/env

Or use the Webmin UI:

Webmin → System Maintenance → Manage GitHub Token