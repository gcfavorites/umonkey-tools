all: run

config:
	gconf-editor /apps/tmradio-client

run:
	./tmradio-client

deb:
	rm -rf *.deb
	mkdir -p debian/usr/bin
	cp tmradio-client debian/usr/bin/tmradio-client
	mkdir -p debian/usr/share/tmradio-client
	cp desktop.ui debian/usr/share/tmradio-client/
	mkdir -p debian/usr/share/gconf/schemas
	cp tmradio.schemas debian/usr/share/gconf/schemas/
	sudo chown -R root:root debian/usr
	dpkg -b debian tmradio-client-gtk-0.2.deb
	sudo rm -rf debian/usr

install: deb
	sudo dpkg -i tmradio-client-gtk-0.2.deb
