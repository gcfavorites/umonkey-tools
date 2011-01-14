VERSION=0.2
DEB=tmradio-client-gtk-${VERSION}.deb

all: run

config:
	gconf-editor /apps/tmradio-client

run:
	./tmradio-client

deb:
	rm -rf *.deb debian/usr
	cat debian/DEBIAN/control.in | sed -e "s/VERSION/${VERSION}/g" > debian/DEBIAN/control
	mkdir -p debian/usr/bin
	cp tmradio-client debian/usr/bin/tmradio-client
	mkdir -p debian/usr/share/tmradio-client
	cp desktop.ui debian/usr/share/tmradio-client/
	mkdir -p debian/usr/share/gconf/schemas
	cp tmradio.schemas debian/usr/share/gconf/schemas/
	sudo chown -R root:root debian/usr
	dpkg -b debian ${DEB}
	sudo rm -rf debian/usr

upload-deb: deb
	googlecode_upload.py -s "Version 0.2 of the GTK+ client for tmradio.net" -p umonkey-tools ${DEB}

install: deb
	sudo dpkg -i ${DEB}
