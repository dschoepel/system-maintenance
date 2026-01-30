#!/bin/bash
set -e

BASE_DIR="/usr/local/system-maintenance"
WEBMIN_DIR="/usr/share/webmin/system-maintenance"

echo "Installing System Maintenance from $BASE_DIR"

# Ensure script is run from repo root if cloned elsewhere
if [ ! -d "$BASE_DIR" ]; then
  echo "Expected repo at $BASE_DIR; creating and copying."
  mkdir -p "$BASE_DIR"
  cp -a . "$BASE_DIR"
fi

# Install maintenance script
install -m 0755 "$BASE_DIR/scripts/system-maintenance.sh" /usr/local/system-maintenance/scripts/system-maintenance.sh

# Install systemd units
install -m 0644 "$BASE_DIR/systemd/system-maintenance.service" /etc/systemd/system/system-maintenance.service
install -m 0644 "$BASE_DIR/systemd/system-maintenance.timer" /etc/systemd/system/system-maintenance.timer
install -m 0644 "$BASE_DIR/systemd/system-maintenance-update.service" /etc/systemd/system/system-maintenance-update.service
install -m 0644 "$BASE_DIR/systemd/system-maintenance-update.timer" /etc/systemd/system/system-maintenance-update.timer

systemctl daemon-reload
systemctl enable --now system-maintenance.timer
# auto-update timer is optional; enable if you want:
# systemctl enable --now system-maintenance-update.timer

# Apply journald template if keys missing
JOURNAL_CONF="/etc/systemd/journald.conf"
if ! grep -q '^SystemMaxUse=' "$JOURNAL_CONF" 2>/dev/null; then
  cat "$BASE_DIR/config/journald.conf.template" >> "$JOURNAL_CONF"
  systemctl restart systemd-journald
fi

# Install Webmin module
mkdir -p "$WEBMIN_DIR"
cp -a "$BASE_DIR/webmin-module/." "$WEBMIN_DIR/"
chmod +x "$WEBMIN_DIR"/*.cgi

# Try to restart Webmin if present
if systemctl status webmin >/dev/null 2>&1; then
  systemctl restart webmin
fi

echo "Installation complete. Open Webmin → System → System Maintenance."
