DOMM_PARSER = build/domm.py
DOMM_FILES = build/*.domm

build:
	mkdir build
	cp -r domm_peg/*.py build
	cp -r domm_peg/*.domm build
	ls

clean:
	rm -rf build

check: build
	python ${DOMM_PARSER} ${DOMM_FILES}
	mv *.dot build
