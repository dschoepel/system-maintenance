#!/usr/bin/perl
# run.cgi — Trigger system maintenance manually
use strict;
use warnings;

use WebminCore;
init_config();

require './system-maintenance-lib.pl';
&ui_print_header(undef, "Run System Maintenance", "");

print &ui_subheading("Executing Maintenance");

# Start the service
run_cmd("systemctl start system-maintenance.service");

# Give systemd a moment
sleep(1);

# Fetch meaningful status output
my $status = run_cmd("systemctl status system-maintenance.service --no-pager -n 10");

# Fetch recent logs
my $logs = run_cmd("journalctl -u system-maintenance.service --no-pager -n 50");

print &ui_table_start("Execution Output", "width=100%");
print &ui_table_row("Service Status", "<pre>$status</pre>");
my $colored = colorize_logs($logs);
print &ui_table_row("Recent Logs", "<pre>$colored</pre>");

print &ui_table_end();

print "<br>";

print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();