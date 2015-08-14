**ddupdate** is a script that updates your dynamic IP when needed.  It compares your current IP with the one known by DynDNS and updates it when necessary.  It uses the DNS protocol and [a public IP detection service](http://checkip.dyndns.org:8245/) to find the addresses, so it must not be a subject for ban because of the periodic activities.

It's very simple: a few lines of bash code, depends on `host` and `wget` binaries.

  * [Source code](http://umonkey-tools.googlecode.com/hg/bin/ddupdate)