#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
require './system-maintenance-lib.pl';

&ui_print_header(undef, "Run Maintenance", "");

print <<'EOF';
<style>
pre span {
    color: inherit !important;
}
.fullwidth {
    width: 100% !important;
    max-width: 100% !important;
}
</style>
EOF

print "<div class='fullwidth'>";
print "<pre style='background:#111;color:#0f0 !important;
       padding:10px;border-radius:6px;height:80vh;overflow:auto;'>";

print "[INFO] Starting system-maintenance.service...\n";
my $out = run_cmd("systemctl start system-maintenance.service");
print colorize_logs($out) . "\n";

print "\n[INFO] Fetching last 50 log lines...\n\n";
my $logs = run_cmd("journalctl -u system-maintenance.service --no-pager -n 50");
print colorize_logs($logs);

print "</pre>";
print "</div>";

print "<br>";
print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();