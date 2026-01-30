#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
header("System Maintenance");

print "<h2>System Maintenance</h2>";

print <<'EOF';
<form method='post' action='run.cgi'>
  <input type='submit' value='Run Cleanup Now'>
</form>

<form method='post' action='install-timer.cgi'>
  <input type='submit' value='Install/Enable Weekly Timer'>
</form>

<form method='post' action='edit-journal.cgi'>
  <input type='submit' value='Edit Journal Limits'>
</form>
EOF

my $apt     = `du -sh /var/cache/apt/archives 2>/dev/null | cut -f1`;
my $journal = `du -sh /var/log/journal 2>/dev/null | cut -f1`;
my $snap    = `snap list --all 2>/dev/null | grep disabled | wc -l`;

chomp($apt);
chomp($journal);
chomp($snap);

print "<h3>Current Status</h3>";
print "<table border=1 cellpadding=5>";
print "<tr><td>APT Cache</td><td>$apt</td></tr>";
print "<tr><td>Journal Size</td><td>$journal</td></tr>";
print "<tr><td>Old Snap Revisions</td><td>$snap</td></tr>";
print "</table>";

footer();
