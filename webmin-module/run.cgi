#!/usr/bin/perl
use strict;
use warnings;

use WebminCore;
init_config();
require './system-maintenance-lib.pl';

&WebminCore::ui_print_header(undef, "Run Maintenance", "", "system-maintenance");

my $output = run_maintenance_once();
my $colored = colorize_logs($output);

print &WebminCore::ui_table_start("Run Output", "width=100%");
print &WebminCore::ui_table_row(
    "Output",
    "<div style='width:100%;max-width:100%;'>
        <pre style='background:#111;color:#0f0 !important;
        padding:10px;border-radius:6px;height:80vh;overflow:auto;'>$colored</pre>
</div>"

);
print &WebminCore::ui_table_end();

print "<br>";
print &WebminCore::ui_link("index.cgi", "Return to Dashboard");

&WebminCore::ui_print_footer();

