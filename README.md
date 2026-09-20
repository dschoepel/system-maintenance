
# System Maintenance (Cockpit + systemd)

A standardized, reproducible disk/log-housekeeping system for Ubuntu servers.
Includes a native Cockpit dashboard page, a weekly systemd timer, and journald size caps.

This repo is public — no token or private-repo auth needed to clone or update it.

---

## Features

### Automated Maintenance
- APT cache cleanup
- Autoremove unused packages
- Snap old revision cleanup
- Journald size caps + vacuuming
- Generic cache cleanup

**Deliberately does *not* run `apt-get upgrade`.** This tool's job is disk/log housekeeping, not
patching — package upgrades belong to a purpose-built mechanism instead: Cockpit's own Software
Updates page (visible, manual, deliberate control) or `unattended-upgrades` (specifically designed
for safe automated patching — security-only by default, reboot-aware — unlike a bare unattended
`apt-get upgrade -y` in a cron script).

### Cockpit Integration
- Dashboard: last run, next scheduled run, last exit code
- Journald caps display (`SystemMaxUse` / `SystemKeepFree` / `MaxFileSec`)
- Colorized (INFO/WARN/ERROR, case-insensitive) log viewer — last 200 lines
- "Run Now" button — genuinely systemd-tracked (`systemctl start`), so a manual run updates the
  same dashboard fields a scheduled run does

### Systemd
- Weekly maintenance timer (`Sun 03:00`)
- On-demand service
- Optional auto-update timer (`system-maintenance-update.timer`, disabled by default — `git pull
  --rebase` on the repo checkout weekly; enable it yourself if you want the repo to self-update)

---

## Installation

No token, no bootstrap script — just clone and run:

```bash
sudo git clone https://github.com/dschoepel/system-maintenance.git /opt/system-maintenance-repo
cd /opt/system-maintenance-repo
sudo bash install.sh
```

This will:

- Install the maintenance script to `/usr/local/system-maintenance/scripts/`
- Install and enable the systemd units
- Apply the journald caps template (only once — won't overwrite an existing `SystemMaxUse=` line)
- Install the Cockpit page to `/usr/share/cockpit/system-maintenance/`

The script is idempotent — safe to re-run.

---

## Updating

```bash
cd /opt/system-maintenance-repo
sudo git pull
sudo bash install.sh
```

This refreshes the systemd units, script, and Cockpit page. Journald config is only ever applied
once (skipped if `SystemMaxUse=` is already set) — your own edits there are preserved.

---

## Cockpit Page

After installation, open **Cockpit → Tools → System Maintenance**. You'll see:

- **Last Run** / **Last Exit Code** / **Next Scheduled Run** — read live via `systemctl show`
- **journald Caps** — read live from `/etc/systemd/journald.conf`
- **Recent Log Output** — last 200 lines of `/var/log/system-maintenance.log`, colorized
- **Run Now** — triggers `systemctl start system-maintenance.service` and refreshes everything
  once it completes

No build tooling needed for the page itself (`cockpit-page/manifest.json`, `index.html`,
`style.css`, `index.js` — plain files, no bundler) — `install.sh` just copies them into place, and
you can redeploy an updated copy the same way (or via Cockpit's own Navigator page, drag-and-drop).

---

## Uninstall

```bash
sudo systemctl disable --now system-maintenance.timer
sudo systemctl disable --now system-maintenance-update.timer   # if you'd enabled it
sudo systemctl disable --now system-maintenance.service

sudo rm -rf /usr/local/system-maintenance
sudo rm -rf /opt/system-maintenance-repo
sudo rm -rf /usr/share/cockpit/system-maintenance
sudo rm -f /etc/systemd/system/system-maintenance*.service /etc/systemd/system/system-maintenance*.timer
sudo systemctl daemon-reload
```

(No service restart needed for the Cockpit page — removing its directory is enough; Cockpit just
won't show the Tools entry on next load.)

---

## Notes

- Designed to be fleet-wide, idempotent, and drift-free — this repo intentionally has no
  host-specific content anywhere (script, systemd units, and Cockpit page are all fully generic).
- Originally built with a Webmin module and a private-repo + GitHub-token install flow; both
  retired 2026-09-20 once the host fleet moved to Cockpit. See `webmin-module/DEPRECATED.md` for
  what changed and why, if you're curious about the history.
