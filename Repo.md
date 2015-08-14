The stuff I write here is available as a debian repository.  To install it, I add the following line to `/etc/apt/sources.list`:

```
deb http://umonkey-tools.googlecode.com/ hg/
```

Then proceed installing particular programs, e.g.:

```
$ sudo apt-get update
$ sudo apt-get install sayhours
```

# TODO #

  * Signing.
    * http://wiki.debian.org/HowToSetupADebianRepository
    * http://wiki.debian.org/SecureApt
    * http://www.google.com/search?sourceid=chrome&ie=UTF-8&q=signing+a+debian+repo