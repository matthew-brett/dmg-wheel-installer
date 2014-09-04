all: clean
	echo ${PWD}
	./make_installer.sh

clean:
	rm -rf pip wheels pkg_template scipy-stack.pkg scripts

install:
	sudo installer -pkg scipy-stack.pkg -verbose -target /
