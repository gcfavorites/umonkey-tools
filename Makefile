update-packages: prepare-files update-release-hash upload-files

prepare-files:
	make -C misc/sayhours upload-deb
	make -C misc/tmradio-client upload-deb
	mkdir -p files
	find -name '*.deb' | egrep -v '^\./files/' | xargs cp --target-directory=files/
	dpkg-scanpackages files | gzip -9c > Packages.gz

update-release-hash:
	grep -v Packages.gz Release > Release.new
	echo " `md5sum Packages.gz | awk '{ print $$1 }'` `ls -l Packages.gz | awk '{ print $$5 }'` Packages.gz" >> Release.new
	mv Release.new Release
	rm -f Release.gpg
	gpg -abs -o Release.gpg Release

upload-files:
	hg ci Packages.gz -m "Packages.gz autoupdate."
	hg push

clean:
	rm -rf files
