#!/usr/bin/perl
use strict;
use warnings;
use WebminCore;

init_config();

my $env_file = "/etc/system-maintenance/env";

# Load existing token (but do NOT display it)
my $token_present = 0;
if (-f $env_file) {
    open(my $fh, "<", $env_file);
    while (<$fh>) {
        if (/^GITHUB_TOKEN=/) {
            my ($k, $v) = split /=/, $_, 2;
            $token_present = ($v && $v !~ /^\s*$/) ? 1 : 0;
        }
    }
    close($fh);
}

# Handle form submission
if ($in{'save'}) {
    my $new_token = $in{'token'};

    # Sanitize whitespace and control chars
    $new_token =~ s/[\r\n\t]//g;

    open(my $fh, ">", $env_file) or die "Cannot write $env_file: $!";
    print $fh "GITHUB_TOKEN=$new_token\n";
    close($fh);

    system("chmod 600 $env_file");

    print &ui_print_header(undef, "Token Updated", "");
    print "<p>The GitHub token has been updated.</p>";
    print &ui_print_footer("/", "Return to module");
    exit;
}

# Render form
print &ui_print_header(undef, "Manage GitHub Token", "");

print "<p>Token status: ";
print $token_present ? "<b>Present</b>" : "<b>Not Set</b>";
print "</p>";

print &ui_form_start("token.cgi");

print &ui_table_start("Update Token", undef, 2);
print &ui_table_row("New Token", &ui_textbox("token", "", 60));
print &ui_table_end();

print &ui_form_end([ [ "save", "Save Token" ] ]);

print &ui_print_footer("/", "Return to module");