# system-maintenance-lib.pl
package system_maintenance;

use strict;
use warnings;

my $JOURNAL_CONF = "/etc/systemd/journald.conf";

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

sub run_cmd {
    my ($cmd) = @_;
    my $out = `$cmd 2>&1`;
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

1;
