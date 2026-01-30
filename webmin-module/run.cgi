#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
header("Running Cleanup");

print "<pre>\n";

system("/usr/local/system-maintenance/scripts/system-maintenance.sh");

print "</pre>\n";
print "<p>Cleanup complete.</p>\n";

footer();
