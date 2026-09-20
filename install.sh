#!/bin/bash
set -e

log() {
    echo -e "\n[INSTALL] $(date '+%Y-%m-%d %H:%M:%S') — $1"
}

REPO_DIR="/opt/system-maintenance-repo"
INSTALL_DIR="/usr/local/system-maintenance"
COCKPIT_DIR="/usr/share/cockpit/system-maintenance"

log "Starting System Maintenance installation from $REPO_DIR"

# Ensure install directory exists
log "Ensuring install directory exists"
mkdir -p "$INSTALL_DIR/scripts"

# Install maintenance script
log "Installing maintenance script"
install -m 0755 "$REPO_DIR/scripts/system-maintenance.sh" "$INSTALL_DIR/scripts/system-maintenance.sh"

# Install systemd units
log "Installing systemd units"
install -m 0644 "$REPO_DIR/systemd/system-maintenance.service" /etc/systemd/system/system-maintenance.service
install -m 0644 "$REPO_DIR/systemd/system-maintenance.timer" /etc/systemd/system/system-maintenance.timer
install -m 0644 "$REPO_DIR/systemd/system-maintenance-update.service" /etc/systemd/system/system-maintenance-update.service
install -m 0644 "$REPO_DIR/systemd/system-maintenance-update.timer" /etc/systemd/system/system-maintenance-update.timer

log "Reloading systemd and enabling timer"
systemctl daemon-reload
systemctl enable --now system-maintenance.timer
# Optional: enable update timer
# systemctl enable --now system-maintenance-update.timer

# journald template
JOURNAL_CONF="/etc/systemd/journald.conf"
if ! grep -q '^SystemMaxUse=' "$JOURNAL_CONF" 2>/dev/null; then
  log "Applying journald template"
  cat "$REPO_DIR/config/journald.conf.template" >> "$JOURNAL_CONF"
  systemctl restart systemd-journald
else
  log "Journald template already applied"
fi

# Install Cockpit page (replaces the old Webmin module -- see
# webmin-module/DEPRECATED.md for history). No build step: just copy the
# four static files into place. Cockpit picks up new Tools pages
# automatically on next browser load, no service restart needed.
log "Installing Cockpit page"
mkdir -p "$COCKPIT_DIR"
cp -a "$REPO_DIR/cockpit-page/." "$COCKPIT_DIR/"
chown -R root:root "$COCKPIT_DIR"
chmod 644 "$COCKPIT_DIR"/*

log "Installation complete"
echo "The System Maintenance page should now appear under Cockpit's Tools menu"
echo "(hard-refresh the browser tab if it doesn't show up immediately)."
