#!/usr/bin/perl
use strict;
use warnings;

use WebminCore;
init_config();
require './system-maintenance-lib.pl';

&WebminCore::ui_print_header(undef, "System Maintenance Status", "", "system-maintenance");

my $logs = read_recent_logs();
my $colored = colorize_logs($logs);

print &WebminCore::ui_table_start("Recent Output", "width=100%");
print &WebminCore::ui_table_row(
    "Logs",
    "<div style='width:100%;max-width:100%;'>
        <pre style='background:#111;color:#0f0 !important;
        padding:10px;border-radius:6px;height:80vh;overflow:auto;'>$colored</pre>
    </div>"
);
print &WebminCore::ui_table_end();

print "<br>";
print &WebminCore::ui_link("index.cgi", "Return to Dashboard");

&WebminCore::ui_print_footer();