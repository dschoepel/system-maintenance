#!/usr/bin/perl
# index.cgi — System Maintenance Dashboard
use strict; 
use warnings; 

use WebminCore; 
init_config();

require './system-maintenance-lib.pl';
&ui_print_header(undef, "System Maintenance Dashboard", "");

print &ui_subheading("Maintenance Status");

# Last run timestamp (from systemd)
my $last_run = `systemctl show system-maintenance.service -p ActiveEnterTimestamp --value 2>/dev/null`;
chomp($last_run);
$last_run = $last_run eq "" ? "No recorded runs yet" : $last_run;

# Next scheduled run (from systemd timer)
my $next_run = `systemctl show system-maintenance.timer -p NextElapseUSecRealtime --value 2>/dev/null`;
chomp($next_run);
$next_run = $next_run eq "" ? "Unknown" : $next_run;

print &ui_table_start("Maintenance Information", "width=100%");
print &ui_table_row("Last Run", $last_run);
print &ui_table_row("Next Scheduled Run", $next_run);
print &ui_table_end();

print "<br>";

print &ui_subheading("Journald Configuration");

my %journal = &read_journald_config();

print &ui_table_start("Journald Caps", "width=100%");
print &ui_table_row("SystemMaxUse", $journal{'SystemMaxUse'});
print &ui_table_row("SystemKeepFree", $journal{'SystemKeepFree'});
print &ui_table_row("MaxFileSec", $journal{'MaxFileSec'});
print &ui_table_end();

print "<br>";

print &ui_subheading("Actions");

print &ui_form_start("run.cgi", "post");
print &ui_submit("Run Maintenance Now");
print &ui_form_end();

print "<br>";

print &ui_link("status.cgi", "View Detailed Status and Logs");

&ui_print_footer();
