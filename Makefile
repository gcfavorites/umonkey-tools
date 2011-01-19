update-packages: prepare-files update-release-hash upload-files

prepare-files:
	make -C misc/sayhours upload-deb
	make -C misc/tmradio-client upload-deb
	mkdir -p files
	find -name '*.deb' | egrep -v '^\./files/' | xargs cp --target-directory=files/
	dpkg-scanpackages files | gzip -9c > Packages.gz

update-release-hash:
	sh bin/update-release-file Packages Packages.gz

upload-files:
	hg ci Packages.gz -m "Packages.gz autoupdate."
	hg push

clean:
	rm -rf files
