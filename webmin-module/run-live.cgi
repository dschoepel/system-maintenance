#!/usr/bin/perl
use strict;
use warnings;
use IO::Handle;
use WebminCore;

init_config();
require './system-maintenance-lib.pl';

# Disable buffering everywhere
$| = 1;
select(STDOUT); $| = 1;

&ui_print_header(undef, "Run Maintenance (Live Output)", "");

# CSS override for Authentic Theme + spinner
print <<'EOF';
<style>
/* Fix Authentic Theme overriding <pre> colors */
pre span {
    color: inherit !important;
}

/* Full-width container */
.fullwidth {
    width: 100% !important;
    max-width: 100% !important;
}

/* Spinner */
.spinner {
  border: 4px solid #333;
  border-top: 4px solid #0f0;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  animation: spin 0.8s linear infinite;
  display:inline-block;
  margin-right:8px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
EOF

print "<div class='spinner'></div> <b>Running maintenance… streaming live output</b><br><br>";

print "<div class='fullwidth'>";
print "<pre style='background:#111;color:#0f0 !important;
       padding:10px;border-radius:6px;height:80vh;overflow:auto;'>";

print "[INFO] Starting system-maintenance.service...\n";
run_cmd("systemctl start system-maintenance.service");

sleep(1);

print "[INFO] Streaming logs...\n\n";

# Open journalctl -f
open(my $fh, "-|", "journalctl -u system-maintenance.service -f --no-pager")
    or die "Cannot stream logs: $!";

my $start = time();

while (my $line = <$fh>) {
    print colorize_logs($line);
    print "<br>\n";      # forces Webmin flush
    STDOUT->flush();     # double flush
    last if time() - $start > 10;
}

close($fh);

print "\n[INFO] Live stream complete.\n";
print "[INFO] Fetching last 50 log lines...\n\n";

my $summary = run_cmd("journalctl -u system-maintenance.service --no-pager -n 50");
print colorize_logs($summary) . "\n";

print "</pre>";
print "</div>";

print "<br>";
print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();