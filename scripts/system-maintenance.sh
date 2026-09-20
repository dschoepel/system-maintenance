#!/bin/bash

###############################################################################
# System Maintenance Script (Fleet‑Ready, Clean Logging, Plain‑Text Output)
###############################################################################

LOGFILE="/var/log/system-maintenance.log"

# Ensure log file exists and is world-readable (the Cockpit page reads it as
# the logged-in user, not necessarily root)
touch "$LOGFILE"
chmod 644 "$LOGFILE"

# Log everything to both stdout (Cockpit's live systemctl-start output) and
# the log file
exec > >(tee -a "$LOGFILE") 2>&1

echo "===== System Maintenance Run: $(date '+%Y-%m-%d %H:%M:%S') ====="

###############################################################################
# APT Maintenance (clean, plain‑text output)
###############################################################################

echo ""
echo "### Updating APT package lists..."
apt-get update -y -o=Dpkg::Use-Pty=0

# Deliberately NOT running `apt-get upgrade` here (removed 2026-09-20). This
# tool's actual job is disk/log housekeeping, not patching -- package
# upgrades belong to a purpose-built mechanism instead: Cockpit's own
# Software Updates page (visible, manual, deliberate) or unattended-upgrades
# (if enabled on a given host; it's specifically designed for safe automated
# patching -- security-only by default, reboot-aware -- unlike a bare
# `apt-get upgrade -y` in a cron script). `apt-get update` above is kept: it
# only refreshes the package index (read-only, no installed-package changes)
# and autoremove below needs current metadata to compute what's safe to drop.

echo ""
echo "### Autoremove unused packages..."
apt-get autoremove -y -o=Dpkg::Use-Pty=0

echo ""
echo "### Autoclean APT cache..."
apt-get autoclean -y -o=Dpkg::Use-Pty=0

###############################################################################
# Journald Vacuuming
###############################################################################

echo ""
echo "### Vacuuming systemd journals..."
journalctl --vacuum-time=7d
journalctl --vacuum-size=200M

###############################################################################
# Snap Cleanup (if snap exists)
###############################################################################

if command -v snap >/dev/null 2>&1; then
    echo ""
    echo "### Cleaning old Snap revisions..."
    snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
        echo "Removing old snap: $snapname ($revision)"
        snap remove "$snapname" --revision="$revision"
    done
fi

###############################################################################
# APT Cache Cleanup
###############################################################################

echo ""
echo "### Cleaning APT cache..."
apt-get clean -y -o=Dpkg::Use-Pty=0

###############################################################################
# Done
###############################################################################

echo ""
echo "===== Maintenance Completed: $(date '+%Y-%m-%d %H:%M:%S') ====="
echo ""
