#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();
header("Edit Journal Limits");

my $conf = "/etc/systemd/journald.conf";

if ($ENV{'REQUEST_METHOD'} eq 'POST') {
    read_parse();
    my $max  = $in{'max'}  || "200M";
    my $keep = $in{'keep'} || "50M";
    my $rt   = $in{'rt'}   || "50M";

    system("grep -q '^SystemMaxUse=' $conf || echo 'SystemMaxUse=$max' >> $conf");
    system("grep -q '^SystemKeepFree=' $conf || echo 'SystemKeepFree=$keep' >> $conf");
    system("grep -q '^RuntimeMaxUse=' $conf || echo 'RuntimeMaxUse=$rt' >> $conf");

    system("sed -i 's/^SystemMaxUse=.*/SystemMaxUse=$max/' $conf");
    system("sed -i 's/^SystemKeepFree=.*/SystemKeepFree=$keep/' $conf");
    system("sed -i 's/^RuntimeMaxUse=.*/RuntimeMaxUse=$rt/' $conf");

    system("systemctl restart systemd-journald");

    print "<p>Journal limits updated.</p>";
}

my $max  = `grep '^SystemMaxUse=' $conf 2>/dev/null | cut -d= -f2`; chomp $max;
my $keep = `grep '^SystemKeepFree=' $conf 2>/dev/null | cut -d= -f2`; chomp $keep;
my $rt   = `grep '^RuntimeMaxUse=' $conf 2>/dev/null | cut -d= -f2`; chomp $rt;

$max  ||= '200M';
$keep ||= '50M';
$rt   ||= '50M';

print <<EOF;
<form method='post'>
SystemMaxUse: <input name='max' value='$max'><br>
SystemKeepFree: <input name='keep' value='$keep'><br>
RuntimeMaxUse: <input name='rt' value='$rt'><br>
<input type='submit' value='Save'>
</form>
EOF

footer();
