###################
DMG wheel installer
###################

A small Python script to generate a dmg disk immage with an OSX .pkg double
click installer to install a given set of Python packages from wheels.

The idea is that any package that can be installed via pip can also have a
safe dmg installer, because we use pip to install the wheels, and pip will
manage the dependencies.

The current installer only installs into Python.org Python, but if there's
anyone out there with good understanding of the pkg format, the given wheels
will also work fine for macports and homebrew, for OSX 10.9.  Actually, they
will work for any OSX >= 10.6, but most people are only naming their wheels to
show their compatibility with 10.9 - see
https://github.com/MacPython/wiki/wiki/Spinning-wheels

Here's how to make an installer for matplotlib 1.4.0::

    ./make_installer.py matplotlib 1.4.0 matplotlib --python-version 3.4

Or for more than one package::

    ./make_installer.py scipy-stack 1.0 scipy matplotlib ipython[notebook] \
        pandas numexpr sympy --python-version 2.7
