all: universal-edit-button-1.oex

clean:
	rm -f tmp.zip universal-edit-button-1.oex

rebuild: clean all

install: all
	cp universal-edit-button-1.oex ${HOME}/.opera/widgets/

universal-edit-button-1.oex: config.xml index.html background.js includes/base.js icons/UEB128.png icons/UEB64.png icons/UEB18.png locales/ru/background.js locales/ru/config.xml
	zip -9 tmp.zip $^
	mv tmp.zip $@
