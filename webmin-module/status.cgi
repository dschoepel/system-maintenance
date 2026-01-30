#!/usr/bin/perl
# status.cgi — Detailed maintenance status and logs

require './system-maintenance-lib.pl';
&ui_print_header(undef, "System Maintenance Status", "");

print &ui_subheading("Maintenance Timing");

my $last_run = get_last_run();
my $next_run = get_next_run();

print &ui_table_start("Run Information", "width=100%");
print &ui_table_row("Last Run", $last_run);
print &ui_table_row("Next Scheduled Run", $next_run);
print &ui_table_end();

print "<br>";

print &ui_subheading("Journald Configuration");

my %journal = read_journald_config();

print &ui_table_start("Journald Caps", "width=100%");
print &ui_table_row("SystemMaxUse",  $journal{'SystemMaxUse'});
print &ui_table_row("SystemKeepFree", $journal{'SystemKeepFree'});
print &ui_table_row("MaxFileSec",    $journal{'MaxFileSec'});
print &ui_table_end();

print "<br>";

print &ui_subheading("Disk Usage Summary");

my $disk = run_cmd("df -h /");
print &ui_table_start("Disk Usage", "width=100%");
print &ui_table_row("Root Filesystem", "<pre>$disk</pre>");
print &ui_table_end();

print "<br>";

print &ui_subheading("Recent Maintenance Logs");

my $logs = run_cmd("journalctl -u system-maintenance.service --no-pager -n 200");

print &ui_table_start("Logs", "width=100%");
print &ui_table_row("Recent Output", "<pre>$logs</pre>");
print &ui_table_end();

print "<br>";

print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();
