
---

### scripts/system-maintenance.sh

```bash
#!/bin/bash
set -e

# Clean APT cache
apt-get clean

# Remove unused packages
apt-get autoremove --purge -y || true

# Vacuum systemd journal to 200MB
journalctl --vacuum-size=200M || true

# Clean snap old revisions
if command -v snap >/dev/null 2>&1; then
  snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
    snap remove "$snapname" --revision="$revision" || true
  done
  snap set system refresh.retain=2 || true
fi

# Clean generic caches
rm -rf /var/cache/*

exit 0
