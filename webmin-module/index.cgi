#!/usr/bin/perl
use strict;
use warnings;

use WebminCore;
init_config();
require './system-maintenance-lib.pl';

&WebminCore::ui_print_header(undef, "System Maintenance Dashboard", "");

print &WebminCore::ui_subheading("Maintenance Status");

my $last_run = `systemctl show system-maintenance.service -p ActiveEnterTimestamp --value 2>/dev/null`;
chomp($last_run);
$last_run = $last_run eq "" ? "No recorded runs yet" : $last_run;

my $next_run = `systemctl show system-maintenance.timer -p NextElapseUSecRealtime --value 2>/dev/null`;
chomp($next_run);
$next_run = $next_run eq "" ? "Unknown" : $next_run;

print &WebminCore::ui_table_start("Maintenance Information", "width=100%");
print &WebminCore::ui_table_row("Last Run", $last_run);
print &WebminCore::ui_table_row("Next Scheduled Run", $next_run);
print &WebminCore::ui_table_end();

print "<br>";

print &WebminCore::ui_subheading("Journald Configuration");

my %journal = read_journald_config();

print &WebminCore::ui_table_start("Journald Caps", "width=100%");
print &WebminCore::ui_table_row("SystemMaxUse",  $journal{'SystemMaxUse'});
print &WebminCore::ui_table_row("SystemKeepFree", $journal{'SystemKeepFree'});
print &WebminCore::ui_table_row("MaxFileSec",    $journal{'MaxFileSec'});
print &WebminCore::ui_table_end();

print "<br>";

print &WebminCore::ui_subheading("Actions");

print &WebminCore::ui_form_start("run.cgi", "post");
print &WebminCore::ui_submit("Run Maintenance Now");
print &WebminCore::ui_form_end();

print "<br>";

print &WebminCore::ui_link("run-live.cgi", "Run Maintenance (Live Output)");
print "<br><br>";

print &WebminCore::ui_link("status.cgi", "View Detailed Status and Logs");

&WebminCore::ui_print_footer();