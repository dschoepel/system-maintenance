// System Maintenance Cockpit page
//
// Ported from the original Webmin module (system_maintenance.pm), with one
// real functional fix: "Run Now" now goes through `systemctl start` instead
// of shelling out to a hardcoded script path directly. The original module
// bypassed systemd entirely, which meant a manual run never updated the
// ActiveEnterTimestamp/ExecMainStatus properties this same dashboard reads
// for "Last Run"/"Last Exit Code" -- only the weekly timer's runs did. Going
// through systemctl makes every run (manual or scheduled) systemd-tracked,
// so the dashboard is now accurate regardless of how a run was triggered.
//
// No GitHub-token management page here (dropped deliberately -- a dedicated
// secrets-editing UI wasn't worth rebuilding for one `nano
// /etc/system-maintenance/env` command in Cockpit's own Terminal tab; see
// this repo's README.md and webmin-module/DEPRECATED.md for more).

(function () {
    "use strict";

    const SERVICE = "system-maintenance.service";
    const TIMER = "system-maintenance.timer";
    const LOG_FILE = "/var/log/system-maintenance.log";
    const JOURNALD_CONF = "/etc/systemd/journald.conf";
    const LOG_TAIL_LINES = "200";

    function el(id) {
        return document.getElementById(id);
    }

    function escapeHtml(s) {
        return s
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    // Same three color tiers as the original Perl module's colorize_logs(), but matched
    // case-insensitively (the /i flag) instead of an enumerated list of exact-case
    // spellings. Confirmed on Neptune Sep 20, 2026: real apt/dpkg/snap output almost
    // always uses Title case ("Warning:", "Err:8", "Failed to fetch") which the original
    // case-sensitive literal list (WARN|Warn|warning|WARNING, etc.) never matched -- so
    // colorization silently never fired on real-world log content. Matching the base word
    // case-insensitively catches every actual case variant instead of guessing at a list.
    function colorize(text) {
        let t = escapeHtml(text);
        t = t.replace(/\b(info)\b/gi, '<span class="lvl-info">$1</span>');
        t = t.replace(/\b(warn|warning)\b/gi, '<span class="lvl-warn">$1</span>');
        t = t.replace(/\b(error|err|fail|failed)\b/gi, '<span class="lvl-error">$1</span>');
        return t;
    }

    function showBanner(kind, msg) {
        const b = el("banner");
        b.className = "banner " + kind;
        b.textContent = msg;
        b.hidden = false;
    }

    function hideBanner() {
        el("banner").hidden = true;
    }

    function showProp(unit, prop) {
        return cockpit
            .spawn(["systemctl", "show", unit, "-p", prop, "--value"], { superuser: "try" })
            .then((out) => out.trim())
            .catch(() => "");
    }

    function refreshStatus() {
        // ActiveEnterTimestamp (what the original Webmin module used) reads back as the
        // literal string "n/a" for this unit even after a real completed run -- confirmed
        // on Neptune Sep 20, 2026. For a Type=oneshot service without RemainAfterExit=yes,
        // that property isn't reliably retained once the unit returns to inactive.
        // ExecMainStartTimestamp is: it's specifically meant to persist as "last invocation"
        // history alongside ExecMainStatus, unlike the more activation-state-oriented
        // ActiveEnterTimestamp.
        // Last Run and Last Exit Code are deliberately gated on the SAME "has this
        // actually run" signal (ExecMainStartTimestamp), not on ExecMainStatus's own
        // emptiness. Confirmed on Mercury Sep 20, 2026 (a genuinely fresh install,
        // service never executed even once): ExecMainStatus reads back "0" -- not an
        // empty string -- for a never-run unit, which would otherwise misreport as
        // "Success (0)" instead of "No recorded runs yet". This wasn't caught during
        // the original Neptune testing because a real run had always already happened
        // there before the page was ever loaded.
        showProp(SERVICE, "ExecMainStartTimestamp").then((startV) => {
            const hasRun = startV && startV !== "n/a";
            el("last-run").textContent = hasRun ? startV : "No recorded runs yet";

            const node = el("last-exit");
            if (!hasRun) {
                node.textContent = "No recorded runs yet";
                node.className = "value";
                return;
            }
            showProp(SERVICE, "ExecMainStatus").then((v) => {
                const n = parseInt(v, 10);
                node.textContent = Number.isNaN(n) ? "Unknown" : n === 0 ? "Success (0)" : "Failed (" + n + ")";
                node.className = "value " + (n === 0 ? "ok" : "bad");
            });
        });

        showProp(TIMER, "NextElapseUSecRealtime").then((v) => {
            el("next-run").textContent = v && v !== "n/a" ? v : "Unknown";
        });
    }

    function refreshJournaldCaps() {
        const caps = { SystemMaxUse: "Not set", SystemKeepFree: "Not set", MaxFileSec: "Not set" };

        cockpit
            .file(JOURNALD_CONF, { superuser: "try" })
            .read()
            .then((content) => {
                (content || "").split("\n").forEach((line) => {
                    line = line.trim();
                    if (!line || line.startsWith("#")) return;
                    const idx = line.indexOf("=");
                    if (idx === -1) return;
                    const key = line.slice(0, idx).trim();
                    const val = line.slice(idx + 1).trim();
                    if (key in caps) caps[key] = val;
                });
            })
            .catch(() => {
                // leave defaults ("Not set") on read failure
            })
            .then(() => {
                el("jc-max-use").textContent = caps.SystemMaxUse;
                el("jc-keep-free").textContent = caps.SystemKeepFree;
                el("jc-max-file-sec").textContent = caps.MaxFileSec;
            });
    }

    function refreshLog() {
        el("log-output").textContent = "Loading…";
        cockpit
            .spawn(["tail", "-n", LOG_TAIL_LINES, LOG_FILE], { superuser: "try" })
            .then((out) => {
                el("log-output").innerHTML = out ? colorize(out) : "No logs found";
                el("log-meta").textContent = "(last " + LOG_TAIL_LINES + " lines)";
                el("log-output").scrollTop = el("log-output").scrollHeight;
            })
            .catch((err) => {
                el("log-output").textContent =
                    "Unable to read log file: " + (err && err.message ? err.message : err);
                el("log-meta").textContent = "";
            });
    }

    function refreshAll() {
        hideBanner();
        refreshStatus();
        refreshJournaldCaps();
        refreshLog();
    }

    function runNow() {
        const btn = el("btn-run");
        btn.disabled = true;
        btn.textContent = "Running…";
        hideBanner();

        cockpit
            .spawn(["systemctl", "start", SERVICE], { superuser: "require" })
            .then(() => {
                showBanner("ok", "Maintenance run completed successfully.");
            })
            .catch((err) => {
                showBanner("bad", "Maintenance run failed: " + (err && err.message ? err.message : err));
            })
            .then(() => {
                btn.disabled = false;
                btn.textContent = "Run Now";
                refreshAll();
            });
    }

    document.addEventListener("DOMContentLoaded", () => {
        el("btn-refresh").addEventListener("click", refreshAll);
        el("btn-run").addEventListener("click", runNow);
        refreshAll();
    });
})();
