# System Maintenance Installer

This document explains how to install the System Maintenance tooling on any Ubuntu server running
Cockpit.

---

## 1. Clone and install

No token needed — this repo is public.

```bash
sudo git clone https://github.com/dschoepel/system-maintenance.git /opt/system-maintenance-repo
cd /opt/system-maintenance-repo
sudo bash install.sh
```

`install.sh` will:

- Install the maintenance script
- Install and enable systemd services and timers
- Install journald configuration (only if not already applied)
- Install the Cockpit page to `/usr/share/cockpit/system-maintenance/`

---

## 2. Verify installation

Check the Cockpit page:

**Cockpit → Tools → System Maintenance**
(hard-refresh the browser tab if the menu entry doesn't appear immediately)

Check the systemd service:

```bash
sudo systemctl status system-maintenance.service
```

Check the timer:

```bash
sudo systemctl list-timers | grep system-maintenance
```

---

## 3. Updating the system

To update to the latest version:

```bash
cd /opt/system-maintenance-repo
sudo git pull
sudo bash install.sh
```
