all: clean
	./make_installer.py scipy-stack 1.0 numpy scipy matplotlib ipython[notebook]

clean:
	rm -rf pip wheels pkg_template scipy-stack.pkg scripts dmg_root *.dmg

install:
	hdiutil attach scipy-stack-py27-1.0.dmg
	sudo installer -pkg /Volumes/scipy-stack-py27-1.0/scipy-stack-1.0.pkg \
	    -verbose -target /
	hdiutil detach /Volumes/scipy-stack-py27-1.0
