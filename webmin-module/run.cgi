#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
require './system-maintenance-lib.pl';

$| = 1;

&ui_print_header(undef, "Run Maintenance (Live Output)", "");

# CSS block using a single-quoted heredoc (NO interpolation)
print <<'EOF';
<style>
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

print "<pre style='background:#111;color:#0f0;padding:10px;border-radius:6px;height:500px;overflow:auto;'>";

print "[INFO] Starting system-maintenance.service...\n";
run_cmd("systemctl start system-maintenance.service");

sleep(1);

print "[INFO] Streaming logs...\n\n";

open(my $fh, "-|", "journalctl -u system-maintenance.service -f --no-pager");

my $start = time();
while (my $line = <$fh>) {
    print colorize_logs($line);
    $| = 1;
    last if time() - $start > 10;
}

close($fh);

print "\n[INFO] Live stream complete.\n";
print "[INFO] Fetching last 50 log lines...\n\n";

my $summary = run_cmd("journalctl -u system-maintenance.service --no-pager -n 50");
print colorize_logs($summary) . "\n";

print "</pre>";

print "<br>";
print &ui_link("index.cgi", "Return to Dashboard");

&ui_print_footer();