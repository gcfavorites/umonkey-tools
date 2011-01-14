VERSION=1.0

deb: clean
	cat debian/DEBIAN/control.in | sed -e "s/VERSION/${VERSION}/g" > debian/DEBIAN/control
	dpkg -b debian sayhours-${VERSION}.deb

upload-deb: deb zip
	-googlecode_upload.py -s "sayhours v${VERSION}" -p umonkey-tools -l Featured,Type-Package,OpSys-Linux sayhours-${VERSION}.deb
	-googlecode_upload.py -s "sayhours v${VERSION}" -p umonkey-tools -l Featured,Type-Source,OpSys-All sayhours-${VERSION}.zip

clean:
	rm -f *deb *zip

zip:
	hg archive -t zip sayhours-${VERSION}.zip
