# Deprecated — replaced by the Cockpit page

As of 2026-09-20, this Webmin module is **no longer installed by `install.sh`** and is not part of
the supported install. It's kept in this repo for historical reference only, not deleted.

Every host this tool ran on has since migrated from Webmin to Cockpit fleet-wide. The dashboard
this module provided (last run / next scheduled run / last exit code, a live-output runner, a
colorized log viewer) has been faithfully re-implemented as a native Cockpit Tools page — see
`../cockpit-page/` — with two real bugs fixed along the way that this module had:

1. Its `run_maintenance_once`/`run_maintenance_live` functions shelled out **directly** to a
   hardcoded script path, completely bypassing systemd — so a manual run through this module never
   updated `ActiveEnterTimestamp`/`ExecMainStatus`, the exact properties `get_last_run()` read. Only
   the weekly timer's runs were ever reflected on the dashboard.
2. Even the timer's own runs wouldn't have shown correctly: `ActiveEnterTimestamp` reads back as
   the literal string `"n/a"` for a `Type=oneshot` unit without `RemainAfterExit=yes` once it
   returns to `inactive` — confirmed directly against a real completed run. `ExecMainStartTimestamp`
   is the property that actually persists as "last invocation" history; the Cockpit page uses that
   instead.
3. `colorize_logs()`'s color rules matched an enumerated list of exact-case spellings
   (`WARN|Warn|warning|WARNING`, etc.) — real apt/dpkg/snap output almost always uses Title case
   (`Warning:`, `Err:8`, `Failed to fetch`), none of which matched character-for-character. The
   Cockpit page matches case-insensitively instead.

The GitHub-token management page (`token.cgi`) was deliberately **not** ported — editing
`/etc/system-maintenance/env` directly (Cockpit's own Terminal tab, or any SSH session) covers the
same need without a dedicated secrets-editing UI, and since this repo is now public, no token is
needed to clone/update it in the first place.

No functional or security reason to delete these files — they're just inert now. Left in place as
a record of the module's original design, in case any of it is useful reference for a future
Cockpit page on some other project.
