package system_maintenance;

use strict;
use warnings;

my $JOURNAL_CONF = "/etc/systemd/journald.conf";

sub read_journald_config {
    my %caps = (
        'SystemMaxUse'   => 'Not set',
        'SystemKeepFree' => 'Not set',
        'MaxFileSec'     => 'Not set'
    );

    if (open(my $fh, "<", $JOURNAL_CONF)) {
        while (my $line = <$fh>) {
            chomp($line);
            next if $line =~ /^\s*#/;
            next if $line !~ /=/;

            my ($key, $val) = split(/\s*=\s*/, $line, 2);
            if (exists $caps{$key}) {
                $caps{$key} = $val;
            }
        }
        close($fh);
    }

    return %caps;
}

sub run_cmd {
    my ($cmd) = @_;
    my $out = qx{$cmd 2>&1};
    chomp($out);
    return $out;
}

sub get_last_run {
    my $ts = run_cmd("systemctl show system-maintenance.service -p ActiveEnterTimestamp --value");
    return $ts eq "" ? "No recorded runs yet" : $ts;
}

sub get_next_run {
    my $ts = run_cmd("systemctl show system-maintenance.timer -p NextElapseUSecRealtime --value");
    return $ts eq "" ? "Unknown" : $ts;
}

sub read_recent_logs {
    my $logfile = "/var/log/system-maintenance.log";

    return "No logs found" if (! -f $logfile);

    my $content = "";
    if (open(my $fh, "<", $logfile)) {
        local $/ = undef;
        $content = <$fh>;
        close($fh);
    } else {
        return "Unable to read log file: $!";
    }

    return $content;
}

sub colorize_logs {
    my ($text) = @_;

    # HTML-safe
    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;

    # Color rules
    $text =~ s/\b(INFO|Info|info)\b/<span style='color:#0f0;font-weight:bold;'>$1<\/span>/g;
    $text =~ s/\b(WARN|Warn|warning|WARNING)\b/<span style='color:#ff0;font-weight:bold;'>$1<\/span>/g;
    $text =~ s/\b(ERROR|Error|error|ERR|FAIL|FAILED)\b/<span style='color:#f33;font-weight:bold;'>$1<\/span>/g;

    return $text;
}

# ------------------------------------------------------------
# Deterministic synchronous execution for Webmin UI
# ------------------------------------------------------------

sub run_maintenance_once {
    # Direct execution of the maintenance script
    my $cmd = "/opt/system-maintenance-repo/scripts/system-maintenance.sh 2>&1";
    my $output = qx{$cmd};
    return $output;
}

sub run_maintenance_live {
    # Same as once — Webmin can't truly stream, so we capture full output
    my $cmd = "/opt/system-maintenance-repo/scripts/system-maintenance.sh 2>&1";
    my $output = qx{$cmd};
    return $output;
}

1;
