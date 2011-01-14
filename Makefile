update-packages:
	make -C misc/sayhours deb
	make -C misc/tmradio-client deb
	mkdir -p files
	find -name '*.deb' | egrep -v '^\./files/' | xargs cp --target-directory=files/
	dpkg-scanpackages files | gzip -9c > Packages.gz
	rm -rf files
