#!/usr/bin/perl
use strict;
use warnings;

use WebminCore;
init_config();
require './system-maintenance-lib.pl';

my $ENV_FILE = "/etc/system-maintenance/env";

sub get_token_status {
    my $status  = "Missing";
    my $details = "No token file found";
    my $valid   = 0;

    if (-f $ENV_FILE) {
        my $token = "";
        if (open(my $fh, "<", $ENV_FILE)) {
            while (my $line = <$fh>) {
                chomp($line);
                next if $line =~ /^\s*#/;
                if ($line =~ /^GITHUB_TOKEN=(.+)$/) {
                    $token = $1;
                    last;
                }
            }
            close($fh);
        }

        if ($token ne "") {
            my $masked = length($token) > 8
                ? substr($token, 0, 4) . "…" . substr($token, -4)
                : "********";

            $status  = "Configured";
            $details = "Token present ($masked)";
            $valid   = 1;
        } else {
            $status  = "Invalid";
            $details = "Token file exists but GITHUB_TOKEN is empty";
            $valid   = 0;
        }
    }

    return ($status, $details, $valid);
}

# Maintenance status
my $last_run = `systemctl show system-maintenance.service -p ActiveEnterTimestamp --value 2>/dev/null`;
chomp($last_run);
$last_run = $last_run eq "" ? "No recorded runs yet" : $last_run;

my $next_run = `systemctl show system-maintenance.timer -p NextElapseUSecRealtime --value 2>/dev/null`;
chomp($next_run);
$next_run = $next_run eq "" ? "Unknown" : $next_run;

# Journald config
my %journal = read_journald_config();

# Token status
my ($token_status, $token_details, $token_valid) = get_token_status();

print "Content-type: text/html\n\n";

print <<"HTML";
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>System Maintenance Dashboard</title>
  <style>
    body { font-family: sans-serif; margin: 20px; }
    h1 { margin-bottom: 0.5rem; }
    h2 { margin-top: 2rem; }
    table { border-collapse: collapse; width: 100%; max-width: 800px; }
    th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
    th { background: #f0f0f0; }
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.85rem;
      font-weight: bold;
      color: #fff;
    }
    .badge-ok { background: #2e7d32; }
    .badge-warn { background: #f9a825; }
    .badge-err { background: #c62828; }
    .warning-box {
      border: 1px solid #f9a825;
      background: #fff8e1;
      padding: 10px;
      margin: 10px 0 20px 0;
      max-width: 800px;
    }
    .actions a, .actions button {
      display: inline-block;
      margin: 4px 8px 4px 0;
      padding: 6px 12px;
      text-decoration: none;
      border-radius: 4px;
      border: 1px solid #1976d2;
      background: #1976d2;
      color: #fff;
      font-size: 0.9rem;
      cursor: pointer;
    }
    .actions a.secondary, .actions button.secondary {
      background: #fff;
      color: #1976d2;
    }
    .actions form { display: inline; }
  </style>
</head>
<body>
  <h1>System Maintenance Dashboard</h1>
HTML

# Token status indicator + warning
my $badge_class = $token_valid ? "badge-ok" : ($token_status eq "Missing" ? "badge-err" : "badge-warn");

print <<"HTML";
  <p>
    <strong>GitHub Token Status:</strong>
    <span class="badge $badge_class">$token_status</span>
    &nbsp; <span>$token_details</span>
  </p>
HTML

if (!$token_valid) {
    print <<"HTML";
  <div class="warning-box">
    <strong>Warning:</strong> The GitHub token is not configured or invalid.
    System-maintenance updates and private repo access may fail.
    Use <em>Manage GitHub Token</em> to configure it, then <em>Test GitHub Access</em>.
  </div>
HTML
}

print <<"HTML";
  <h2>Maintenance Status</h2>
  <table>
    <tr><th>Last Run</th><td>$last_run</td></tr>
    <tr><th>Next Scheduled Run</th><td>$next_run</td></tr>
  </table>

  <h2>Journald Configuration</h2>
  <table>
    <tr><th>SystemMaxUse</th><td>$journal{SystemMaxUse}</td></tr>
    <tr><th>SystemKeepFree</th><td>$journal{SystemKeepFree}</td></tr>
    <tr><th>MaxFileSec</th><td>$journal{MaxFileSec}</td></tr>
  </table>

  <h2>Actions</h2>
  <div class="actions">
    <form action="run.cgi" method="post">
      <button type="submit">Run Maintenance Now</button>
    </form>

    <a href="run-live.cgi">Run Maintenance (Live Output)</a>
    <a href="status.cgi" class="secondary">View Detailed Status and Logs</a>
    <a href="token.cgi" class="secondary">Manage GitHub Token</a>

    <form action="token.cgi" method="get">
      <input type="hidden" name="action" value="test">
      <button type="submit" class="secondary">Test GitHub Access</button>
    </form>
  </div>
</body>
</html>
HTML

exit 0;
