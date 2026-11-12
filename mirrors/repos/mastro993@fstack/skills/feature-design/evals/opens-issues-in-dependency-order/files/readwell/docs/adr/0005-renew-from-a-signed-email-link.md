# Members renew from a signed link in the reminder email, without logging in

Most members never log in, so a renew button behind the login would go unused. Each reminder email
carries a link that is valid for that one loan until its due date and is signed with a server
secret, so it can't be guessed or reused for another loan. Opening the link shows a confirm page;
only pressing Renew there renews, because mail scanners open links on their own.

Considered: a login-gated button (the friction we are removing); renewing on link open (scanners
would renew every loan).
