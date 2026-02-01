
# System Maintenance (Webmin + systemd)

A standardized, reproducible maintenance system for Ubuntu servers.  
Includes a Webmin UI, systemd timers, journald caps, Snap cleanup, and a secure Git‑based update workflow.

This repository contains the **private code** (systemd units, scripts, Webmin module).  
Installation is performed using a **public bootstrap installer** hosted as a GitHub Gist.

---

## Features

### Automated Maintenance
- APT cache cleanup  
- Autoremove unused packages  
- Snap old revision cleanup  
- Journald size caps + vacuuming  
- Generic cache cleanup  

### Webmin Integration
- Dashboard (status, next run, exit code)  
- Live output runner with spinner  
- Colorized log viewer (INFO/WARN/ERROR)  
- Token management UI  
- Detailed status page  

### Systemd
- Weekly maintenance timer  
- On‑demand service  
- Optional auto‑update timer  

### Security
- GitHub token stored locally in `/etc/system-maintenance/env`  
- Token never displayed in UI  
- Repo remains private  
- Bootstrap installer contains no secrets  

---

## Installation

### 1. Create the token file

```bash
sudo mkdir -p /etc/system-maintenance
sudo chmod 700 /etc/system-maintenance
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxx" | sudo tee /etc/system-maintenance/env > /dev/null
sudo chmod 600 /etc/system-maintenance/env
```

The token must have **read access** to this private repo.

---

### 2. Run the public bootstrap installer

```bash
curl -fsSL https://gist.githubusercontent.com/dschoepel/f6a133d9ef557d79e56f9f62bd01b5e1/raw/bootstrap.sh | sudo bash
```

This will:

- Install git if missing  
- Clone or update this private repo  
- Run `install.sh`  
- Install systemd units  
- Install journald config (idempotent)  
- Install the Webmin module  
- Restart Webmin if running  

The installer is **idempotent** and safe to run repeatedly.

---

## Updating

To update the system:

```bash
cd /opt/system-maintenance-repo
sudo git pull
sudo bash install.sh
```

This refreshes:

- systemd units  
- Webmin module  
- scripts  
- journald config (only once)  

User settings are preserved.

---

## Webmin Module

After installation, open:

**Webmin → System Maintenance**

You will see:

### Dashboard
- Last run  
- Next scheduled run  
- Last exit code  
- Journald caps  
- Run Now  
- Run with Live Output  
- View Detailed Status  

### Manage GitHub Token
- Update token securely  
- Token presence indicator  
- Sanitized input  
- Secure storage  

### Live Output Runner
- Spinner animation  
- Real‑time log streaming  
- Colorized severity (INFO/WARN/ERROR)  
- Final summary  

---

## Uninstall

```bash
sudo systemctl disable --now system-maintenance.timer
sudo systemctl disable --now system-maintenance.service

sudo rm -rf /usr/local/system-maintenance
sudo rm -rf /opt/system-maintenance-repo
sudo rm -rf /etc/system-maintenance
sudo rm -rf /usr/share/webmin/system-maintenance

sudo rm -f /etc/webmin/module.infos.cache
sudo systemctl restart webmin
```

---

## Notes

- The bootstrap installer is public and contains **no secrets**.  
- The GitHub token is stored securely and never shown in the UI.  
- The system is designed to be **fleet‑wide**, **idempotent**, and **drift‑free**.  
- All Webmin module files are installed under `/usr/share/webmin/system-maintenance`.  