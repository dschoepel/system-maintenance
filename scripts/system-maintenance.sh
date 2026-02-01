#!/bin/bash

###############################################################################
# System Maintenance Script (Fleet‑Ready, Clean Logging, Plain‑Text Output)
###############################################################################

LOGFILE="/var/log/system-maintenance.log"

# Ensure log file exists and is readable by Webmin
touch "$LOGFILE"
chmod 644 "$LOGFILE"

# Log everything to both stdout (Webmin Live Output) and the log file
exec > >(tee -a "$LOGFILE") 2>&1

echo "===== System Maintenance Run: $(date '+%Y-%m-%d %H:%M:%S') ====="

###############################################################################
# APT Maintenance (clean, plain‑text output)
###############################################################################

echo ""
echo "### Updating APT package lists..."
apt-get update -y -o=Dpkg::Use-Pty=0

echo ""
echo "### Upgrading installed packages..."
apt-get upgrade -y -o=Dpkg::Use-Pty=0

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
