# system-maintenance-lib.pl
# Shared helpers for the System Maintenance Webmin module
package system_maintenance;

use strict;
use warnings;

# Webmin core
require 'web-lib.pl';
require 'ui-lib.pl';

# Path to journald config
my $JOURNAL_CONF = "/etc/systemd/journald.conf";

# ------------------------------------------------------------
# read_journald_config()
# Returns a hash of journald caps (SystemMaxUse, SystemKeepFree, MaxFileSec)
# ------------------------------------------------------------
sub read_journald_config {
    my %caps = (
        'SystemMaxUse'  => 'Not set',
        'SystemKeepFree'=> 'Not set',
        'MaxFileSec'    => 'Not set'
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

# ------------------------------------------------------------
# run_cmd($cmd)
# Safely run a shell command and return output
# ------------------------------------------------------------
sub run_cmd {
    my ($cmd) = @_;
    my $out = `$cmd 2>&1`;
    chomp($out);
    return $out;
}

# ------------------------------------------------------------
# get_last_run()
# Returns last run timestamp from systemd
# ------------------------------------------------------------
sub get_last_run {
    my $ts = run_cmd("systemctl show system-maintenance.service -p ActiveEnterTimestamp --value");
    return $ts eq "" ? "No recorded runs yet" : $ts;
}

# ------------------------------------------------------------
# get_next_run()
# Returns next scheduled run from systemd timer
# ------------------------------------------------------------
sub get_next_run {
    my $ts = run_cmd("systemctl show system-maintenance.timer -p NextElapseUSecRealtime --value");
    return $ts eq "" ? "Unknown" : $ts;
}

1;  # Required for Webmin library modules
