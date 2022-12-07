#!/usr/bin/expect
set timeout 10
spawn telnet localhost 25
expect {
    timeout { exit 1 }
    eof     { exit 1 }
    "ESMTP"
}
send "quit\n"
expect {
    timeout { exit 1 }
    eof     { exit 1 }
    "Bye"
}
