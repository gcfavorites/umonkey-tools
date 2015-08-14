**sayhours** is a script that speaks current time (hours only) in Russian.  Unlike [saytime](http://linux.maruhn.com/sec/saytime.html), the samples are well processed.  The script is designed to be run as a cron job.

The package contains several samples for each hour, both male and female, chosen randomly each time.

More samples are welcome.

# Installing under Linux #

```
$ wget http://umonkey-tools.googlecode.com/files/sayhours-1.0.deb
$ sudo dpkg -i sayhours-1.0.deb
```

Or use [the repo](Repo.md):

```
$ sudo apt-get install sayhours
```

Adding the cron job:

```
$ crontab -l > ct
$ echo "0 7-23 * * * sayhours" >> ct
$ crontab < ct
$ rm ct
```

With this setup the time will be spoken at the beginning of every hour from 7AM until 11PM.  Adjust the hours as you like.

# Source code #

[See the Mercurial repo](http://code.google.com/p/umonkey-tools/source/browse/misc/sayhours/debian/usr/bin/sayhours).

# Adding voices #

The samples live in `/usr/share/sayhours/??/*.ogg`, where "??" is the hour, 00 to 24.  Just drop your WAV, OGG or FLAC files there.

# Contributing #

Record 1-2 samples for each of the 24 hours and send the WAVs or FLACs to [justin.forest@gmail.com](mailto:justin.forest@gmail.com).