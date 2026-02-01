#!/usr/bin/perl
use strict;
use warnings;

use WebminCore;
init_config();
require './system-maintenance-lib.pl';

&WebminCore::ui_print_header(undef, "Run Maintenance", "", "system-maintenance", undef, 1);


my $output = run_maintenance_once();
my $colored = colorize_logs($output);

print qq{
  <h2>Run Output</h2>
  <div style="width:100%;max-width:100%;">
    <pre style="background:#111;color:#0f0 !important;
      padding:10px;border-radius:6px;height:80vh;overflow:auto;">
$colored
    </pre>
  </div>
};


print "<br>";
print &WebminCore::ui_link("index.cgi", "Return to Dashboard");

&WebminCore::ui_print_footer();

