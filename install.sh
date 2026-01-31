#!/bin/bash
set -e

BASE_DIR="/usr/local/system-maintenance"
WEBMIN_DIR="/usr/share/webmin/system-maintenance"
WEBMIN_ETC="/etc/webmin/system-maintenance"

echo "Installing System Maintenance from $BASE_DIR"

# Ensure base directory exists
mkdir -p "$BASE_DIR"

# Install maintenance script
install -m 0755 scripts/system-maintenance.sh "$BASE_DIR/scripts/system-maintenance.sh"

# Install systemd units
install -m 0644 "$BASE_DIR/systemd/system-maintenance.service" /etc/systemd/system/system-maintenance.service
install -m 0644 "$BASE_DIR/systemd/system-maintenance.timer" /etc/systemd/system/system-maintenance.timer
install -m 0644 "$BASE_DIR/systemd/system-maintenance-update.service" /etc/systemd/system/system-maintenance-update.service
install -m 0644 "$BASE_DIR/systemd/system-maintenance-update.timer" /etc/systemd/system/system-maintenance-update.timer

systemctl daemon-reload
systemctl enable --now system-maintenance.timer

# journald template
JOURNAL_CONF="/etc/systemd/journald.conf"
if ! grep -q '^SystemMaxUse=' "$JOURNAL_CONF" 2>/dev/null; then
  echo "Applying journald template..."
  cat "$BASE_DIR/config/journald.conf.template" >> "$JOURNAL_CONF"
  systemctl restart systemd-journald
fi

# Install Webmin module
echo "Installing Webmin module..."
rm -rf "$WEBMIN_DIR"
mkdir -p "$WEBMIN_DIR"
cp -a "$BASE_DIR/webmin-module/." "$WEBMIN_DIR/"
chmod +x "$WEBMIN_DIR"/*.cgi

# Install Webmin config
mkdir -p "$WEBMIN_ETC"
cp "$BASE_DIR/webmin-module/config" "$WEBMIN_ETC/config"
chmod 600 "$WEBMIN_ETC/config"

# Clear Webmin module cache
rm -f /etc/webmin/module.infos.cache

# Restart Webmin
if systemctl status webmin >/dev/null 2>&1; then
  systemctl restart webmin
fi

echo "Installation complete."
echo "IMPORTANT: Grant yourself access in Webmin → Webmin Users → Available Modules → System Maintenance"
