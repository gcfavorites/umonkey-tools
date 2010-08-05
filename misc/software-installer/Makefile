all: umonkey-tools.deb

umonkey-tools.deb: debian/DEBIAN/control
	dpkg -b debian umonkey-tools.deb

install: umonkey-tools.deb
	sudo gdebi -n umonkey-tools.deb
