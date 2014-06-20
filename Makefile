DOMM_PARSER = build/parser.py
DOMM_FILES = build/*.domm

build:
	mkdir build
	cp -r domm/*.py build
	cp -r domm/*.domm build

clean:
	rm -rf build

check: clean build
	python ${DOMM_PARSER} ${DOMM_FILES}
	mv *.dot build
