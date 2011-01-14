update-packages:
	make -C misc/sayhours upload-deb
	make -C misc/tmradio-client upload-deb
	mkdir -p files
	find -name '*.deb' | egrep -v '^\./files/' | xargs cp --target-directory=files/
	dpkg-scanpackages files | gzip -9c > Packages.gz
	rm -rf files
	hg ci Packages.gz -m "Packages.gz autoupdate."
	hg push
