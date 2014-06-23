BUILD_FOLDER = build
DOMM_PARSER = ${BUILD_FOLDER}/parser.py
DOMM_FILES = ${BUILD_FOLDER}/*.domm

build:
	mkdir ${BUILD_FOLDER}
	cp -r domm/domm/*.py ${BUILD_FOLDER}
	cp -r domm/domm/*.domm ${BUILD_FOLDER}

clean:
	rm -rf ${BUILD_FOLDER}

check: clean build
	python ${DOMM_PARSER} ${DOMM_FILES}
	mv *.dot ${BUILD_FOLDER}
