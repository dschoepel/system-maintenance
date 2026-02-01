#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
require './system-maintenance-lib.pl';

&ui_print_header(undef, "System Maintenance Status", "");

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

my %caps = read_journald_config();
my $last = get_last_run();
my $next = get_next_run();

print "<div class='fullwidth'>";

print &ui_table_start("Maintenance Information", "width=100%");
print &ui_table_row("Last Run", $last);
print &ui_table_row("Next Scheduled Run", $next);
print &ui_table_row("SystemMaxUse", $caps{'SystemMaxUse'});
print &ui_table_row("SystemKeepFree", $caps{'SystemKeepFree'});
print &ui_table_row("MaxFileSec", $caps{'MaxFileSec'});
print &ui_table_end();

print "<br>";

my $logs = run_cmd("journalctl -u system-maintenance.service --no-pager -n 100");
my $colored = colorize_logs($logs);

print &ui_table_start("Recent Output", "width=100%");
print &ui_table_row("Logs",
    &ui_raw("<pre style='background:#111;color:#0f0 !important;
             padding:10px;border-radius:6px;height:80vh;overflow:auto;'>$colored</pre>")
);
print &ui_table_end();

print "</div>";

print "<br>";
print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();