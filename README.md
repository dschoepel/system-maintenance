# System Maintenance (Webmin + systemd)

Standardized maintenance for Ubuntu servers:

- APT cache cleanup
- Autoremove unused packages
- Systemd journal vacuum + size caps
- Snap old revision cleanup + retention
- Generic cache cleanup
- Webmin module UI
- Weekly systemd timer
- Optional Git auto-update timer

## Install

```bash

sudo git clone https://<your-remote>/system-maintenance.git /usr/local/system-maintenance

cd /usr/local/system-maintenance

sudo bash install.sh