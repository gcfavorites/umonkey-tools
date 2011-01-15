VERSION=0.5
DEB=tmradio-client-gtk-${VERSION}.deb
ZIP=tmradio-client-gtk-${VERSION}.zip

all: test

config:
	gconf-editor /apps/tmradio-client

test:
	./tmradio-client

debug:
	./tmradio-client --debug

clean:
	rm -f *.zip *.deb

deb:
	rm -rf *.deb debian/usr
	cat debian/DEBIAN/control.in | sed -e "s/VERSION/${VERSION}/g" > debian/DEBIAN/control
	mkdir -p debian/usr/bin
	cp tmradio-client debian/usr/bin/tmradio-client
	mkdir -p debian/usr/share/tmradio-client
	cp data/ui/*.ui debian/usr/share/tmradio-client/
	mkdir -p debian/usr/share/icons/hicolor/48x48/apps
	cp data/logo-48x48.png debian/usr/share/icons/hicolor/48x48/apps/tmradio-client.png
	mkdir -p debian/usr/share/gconf/schemas
	cp data/tmradio.schemas debian/usr/share/gconf/schemas/
	mkdir -p debian/usr/share/applications
	cp data/tmradio.desktop debian/usr/share/applications/
	sudo chown -R root:root debian/usr
	dpkg -b debian ${DEB}
	sudo rm -rf debian/usr

zip:
	zip -9 ${ZIP} tmradio-client data Makefile

upload-deb: deb zip
	-googlecode_upload.py -s "Version ${VERSION} of the GTK+ client for tmradio.net" -p umonkey-tools -l tmradio ${DEB}
	-googlecode_upload.py -s "Version ${VERSION} of the GTK+ client for tmradio.net" -p umonkey-tools -l tmradio ${ZIP}

install: deb
	sudo dpkg -i ${DEB}

release:
	make -C ../.. update-packages
