#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
require './system-maintenance-lib.pl';

&WebminCore::ui_print_header(undef, "System Maintenance Status", "");

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

print &WebminCore::ui_table_start("Maintenance Information", "width=100%");
print &WebminCore::ui_table_row("Last Run", $last);
print &WebminCore::ui_table_row("Next Scheduled Run", $next);
print &WebminCore::ui_table_row("SystemMaxUse", $caps{'SystemMaxUse'});
print &WebminCore::ui_table_row("SystemKeepFree", $caps{'SystemKeepFree'});
print &WebminCore::ui_table_row("MaxFileSec", $caps{'MaxFileSec'});
print &WebminCore::ui_table_end();

print "<br>";

my $logs    = run_cmd("journalctl -u system-maintenance.service --no-pager -n 100");
my $colored = colorize_logs($logs);

print &WebminCore::ui_table_start("Recent Output", "width=100%");
print &WebminCore::ui_table_row(
    "Logs",
    &WebminCore::ui_raw(
        "<pre style='background:#111;color:#0f0 !important;
         padding:10px;border-radius:6px;height:80vh;overflow:auto;'>$colored</pre>"
    )
);
print &WebminCore::ui_table_end();

print "</div>";

print "<br>";
print &WebminCore::ui_link("index.cgi", "Return to Dashboard");

&WebminCore::ui_print_footer();
