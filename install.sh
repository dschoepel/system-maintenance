#!/bin/bash
set -e

log() {
    echo -e "\n[INSTALL] $(date '+%Y-%m-%d %H:%M:%S') — $1"
}

BASE_DIR="/usr/local/system-maintenance"
WEBMIN_DIR="/usr/share/webmin/system-maintenance"
WEBMIN_ETC="/etc/webmin/system-maintenance"

log "Starting System Maintenance installation from $BASE_DIR"

# Ensure base directory exists
log "Ensuring base directory exists"
mkdir -p "$BASE_DIR"

# Install maintenance script
log "Installing maintenance script"
install -m 0755 scripts/system-maintenance.sh "$BASE_DIR/scripts/system-maintenance.sh"

# Install systemd units
log "Installing systemd units"
install -m 0644 "$BASE_DIR/systemd/system-maintenance.service" /etc/systemd/system/system-maintenance.service
install -m 0644 "$BASE_DIR/systemd/system-maintenance.timer" /etc/systemd/system/system-maintenance.timer
install -m 0644 "$BASE_DIR/systemd/system-maintenance-update.service" /etc/systemd/system/system-maintenance-update.service
install -m 0644 "$BASE_DIR/systemd/system-maintenance-update.timer" /etc/systemd/system/system-maintenance-update.timer

log "Reloading systemd and enabling timer"
systemctl daemon-reload
systemctl enable --now system-maintenance.timer

# journald template
JOURNAL_CONF="/etc/systemd/journald.conf"
if ! grep -q '^SystemMaxUse=' "$JOURNAL_CONF" 2>/dev/null; then
  log "Applying journald template"
  cat "$BASE_DIR/config/journald.conf.template" >> "$JOURNAL_CONF"
  systemctl restart systemd-journald
else
  log "Journald template already applied"
fi

# Install Webmin module
log "Installing Webmin module"
rm -rf "$WEBMIN_DIR"
mkdir -p "$WEBMIN_DIR"
cp -a "$BASE_DIR/webmin-module/." "$WEBMIN_DIR/"
chmod 755 "$WEBMIN_DIR"/*.cgi
chmod 644 "$WEBMIN_DIR"/*.pl
chmod 644 "$WEBMIN_DIR/module.info"

# REQUIRED: module-local config file
log "Creating Webmin module config file"
echo "desc=System Maintenance" > "$WEBMIN_DIR/config"
chmod 644 "$WEBMIN_DIR/config"

# REQUIRED: lang/en file
log "Creating Webmin module lang/en file"
mkdir -p "$WEBMIN_DIR/lang"
echo "desc=System Maintenance" > "$WEBMIN_DIR/lang/en"
chmod 644 "$WEBMIN_DIR/lang/en"

# Install Webmin ETC config (user settings)
log "Installing Webmin ETC config"
mkdir -p "$WEBMIN_ETC"
cp "$BASE_DIR/webmin-module/config" "$WEBMIN_ETC/config"
chmod 600 "$WEBMIN_ETC/config"

# Clear Webmin module cache
log "Clearing Webmin module cache"
rm -f /etc/webmin/module.infos.cache

# Restart Webmin
if systemctl status webmin >/dev/null 2>&1; then
  log "Restarting Webmin"
  systemctl restart webmin
else
  log "Webmin not running — skipping restart"
fi

log "Installation complete"
echo "IMPORTANT: Grant yourself access in Webmin → Webmin Users → Available Modules → System Maintenance"
