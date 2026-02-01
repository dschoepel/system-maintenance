#!/usr/bin/perl
use strict;
use warnings;

use WebminCore;
init_config();

my $ENV_FILE = "/etc/system-maintenance/env";

sub read_token {
    return ("Missing", "", "No token file found")
        if (! -f $ENV_FILE);

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

    if ($token eq "") {
        return ("Invalid", "", "Token file exists but GITHUB_TOKEN is empty");
    }

    my $masked = length($token) > 8
        ? substr($token, 0, 4) . "…" . substr($token, -4)
        : "********";

    return ("Configured", $token, "Token present ($masked)");
}

sub write_token {
    my ($token) = @_;

    my $dir = "/etc/system-maintenance";
    if (! -d $dir) {
        mkdir $dir, 0755 or return "Failed to create $dir: $!";
    }

    if (!open(my $fh, ">", $ENV_FILE)) {
        return "Unable to write $ENV_FILE: $!";
    }

    print $fh "GITHUB_TOKEN=$token\n";
    close($fh);

    chmod 0600, $ENV_FILE;

    return "";
}

sub test_github_access {
    my ($token) = @_;
    return ("error", "No token configured") if !$token;

    my $cmd = "curl -s -o /dev/null -w '%{http_code}' ".
              "-H 'Authorization: Bearer $token' ".
              "-H 'Accept: application/vnd.github+json' ".
              "https://api.github.com/user 2>/dev/null";

    my $code = `$cmd`;
    chomp($code);

    if ($code eq "200") {
        return ("ok", "GitHub access successful (HTTP 200 from /user)");
    } elsif ($code eq "401") {
        return ("error", "GitHub returned 401 Unauthorized. Token is invalid or lacks required scopes.");
    } elsif ($code eq "") {
        return ("error", "No response from GitHub. Check network connectivity and curl availability.");
    } else {
        return ("error", "GitHub returned HTTP $code. Token may be invalid or missing permissions.");
    }
}

# Parse params
my %in;
&ReadParse(\%in);

my $action = $in{'action'} || "";
my $message = "";
my $message_type = ""; # "ok" or "error"

if ($action eq "save") {
    my $new_token = $in{'token'} // "";
    $new_token =~ s/^\s+|\s+$//g;

    if ($new_token eq "") {
        $message = "Token cannot be empty.";
        $message_type = "error";
    } else {
        my $err = write_token($new_token);
        if ($err ne "") {
            $message = $err;
            $message_type = "error";
        } else {
            $message = "Token updated successfully.";
            $message_type = "ok";
        }
    }
}
elsif ($action eq "test") {
    my ($status, $token, $details) = read_token();
    if ($status ne "Configured") {
        $message = "Cannot test GitHub access: $details";
        $message_type = "error";
    } else {
        my ($res, $msg) = test_github_access($token);
        $message = $msg;
        $message_type = $res;
    }
}

my ($token_status, $current_token, $token_details) = read_token();
my $masked = $token_status eq "Configured"
    ? ($token_details =~ /\((.+)\)/ ? $1 : "********")
    : "";

print "Content-type: text/html\n\n";

my $badge_class = $token_status eq "Configured"
    ? "badge-ok"
    : ($token_status eq "Missing" ? "badge-err" : "badge-warn");

print <<"HTML";
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Manage GitHub Token</title>
  <style>
    body { font-family: sans-serif; margin: 20px; }
    h1 { margin-bottom: 0.5rem; }
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
    .message {
      border-radius: 4px;
      padding: 8px 10px;
      margin: 10px 0 20px 0;
      max-width: 800px;
    }
    .message-ok { border: 1px solid #2e7d32; background: #e8f5e9; }
    .message-error { border: 1px solid #c62828; background: #ffebee; }
    label { display: block; margin-top: 10px; }
    input[type="text"], input[type="password"] {
      width: 100%;
      max-width: 600px;
      padding: 6px 8px;
      margin-top: 4px;
      box-sizing: border-box;
    }
    button {
      margin-top: 12px;
      padding: 6px 12px;
      border-radius: 4px;
      border: 1px solid #1976d2;
      background: #1976d2;
      color: #fff;
      cursor: pointer;
      font-size: 0.9rem;
    }
    button.secondary {
      background: #fff;
      color: #1976d2;
    }
    .actions { margin-top: 10px; }
    .actions form { display: inline; }
    a.back-link {
      display: inline-block;
      margin-top: 20px;
      text-decoration: none;
      color: #1976d2;
    }
  </style>
</head>
<body>
  <h1>Manage GitHub Token</h1>
  <p>
    <strong>Status:</strong>
    <span class="badge $badge_class">$token_status</span>
    &nbsp; <span>$token_details</span>
  </p>
HTML

if ($message ne "") {
    my $cls = $message_type eq "ok" ? "message-ok" : "message-error";
    print <<"HTML";
  <div class="message $cls">
    $message
  </div>
HTML
}

my $value_attr = $current_token ne "" ? " value=\"\"" : "";
my $placeholder = $current_token ne "" ? "Leave blank to keep existing token" : "Enter GitHub fine-grained token";

print <<"HTML";
  <form action="token.cgi" method="post">
    <input type="hidden" name="action" value="save">
    <label for="token">GitHub Token</label>
    <input type="password" id="token" name="token" placeholder="$placeholder"$value_attr>
    <div class="actions">
      <button type="submit">Save Token</button>
    </div>
  </form>

  <div class="actions">
    <form action="token.cgi" method="get">
      <input type="hidden" name="action" value="test">
      <button type="submit" class="secondary">Test GitHub Access</button>
    </form>
  </div>

  <a href="index.cgi" class="back-link">&larr; Back to System Maintenance Dashboard</a>
</body>
</html>
HTML

exit 0;

