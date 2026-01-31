#!/usr/bin/perl
# run.cgi — Trigger system maintenance manually
use strict; 
use warnings; 

use WebminCore; 
init_config();

require './system-maintenance-lib.pl';
&ui_print_header(undef, "Run System Maintenance", "");

print &ui_subheading("Executing Maintenance");

# Run the systemd service
my $output = run_cmd("systemctl start system-maintenance.service");

# Give systemd a moment to start the job
sleep(1);

# Fetch recent logs from the service
my $logs = run_cmd("journalctl -u system-maintenance.service --no-pager -n 50");

print &ui_table_start("Execution Output", "width=100%");
print &ui_table_row("Systemd Response", "<pre>$output</pre>");
print &ui_table_row("Recent Logs", "<pre>$logs</pre>");
print &ui_table_end();

print "<br>";

print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();

