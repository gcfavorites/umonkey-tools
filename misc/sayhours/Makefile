VERSION=1.0

deb: clean
	cat debian/DEBIAN/control.in | sed -e "s/VERSION/${VERSION}/g" > debian/DEBIAN/control
	dpkg -b debian saytime-${VERSION}.deb

clean:
	rm -f *deb
