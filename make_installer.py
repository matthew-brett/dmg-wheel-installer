#!/usr/bin/env python
""" Make dmg installer for Python.org Python from Python wheels """
from __future__ import division, print_function

DESCRIP = "Make dmg installer for Python.org Python from Python wheels"
EPILOG = \
"""Make DMG installer from wheels

* Collect source packages for pip, setuptools
* Collect needed wheels using "pip wheel" command
* Write directory to DMG containing source and wheel packages
* Write "postinstall" script to install setuptools, pip, then install wheels
* Write "postinstall" script in ".pkg" double click installer
* Package result into DMG file.
"""

import os
from os.path import exists, join as pjoin
import shutil
from subprocess import check_call
from argparse import ArgumentParser, RawDescriptionHelpFormatter
try:
    from urllib2 import urlopen, URLError # Python 2
except ImportError:
    from urllib.request import urlopen, URLError # Python 3

# Defaults
PYTHON_VERSION='2.7'

# Constants
# Installed location of Python.org Python
PY_ORG_BASE='/Library/Frameworks/Python.framework/Versions/'
# Path for directory that will become the dmg contents
DMG_DIR='dmg_root'
# Subdirectory containing wheels and source packages
PKG_DIR = 'packages'
# Package directory within dmg_directory
DMG_PKG_DIR = DMG_DIR + '/' + PKG_DIR
# get-pip.py URL
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'


def rm_mk_dir(dirname):
    if exists(dirname):
        shutil.rmtree(dirname)
    os.makedirs(dirname)


def mkdirs():
    [rm_mk_dir(pth) for pth in (
        DMG_PKG_DIR,
        'scripts',
        'pkg_template')]


def get_pip_params(args):
    params = '--no-index' if args.no_index else []
    for link in args.find_links:
        params.append('--find-links=' + link)
    return params


def get_pippers(pip_params, get_pip_path=None):
    pip_cmd = ['pip', 'install',
               '--download', DMG_PKG_DIR,
               'pip', 'setuptools'] + pip_params
    check_call(pip_cmd)
    if not get_pip_path is None:
        shutil.copy2(get_pip_path, DMG_PKG_DIR)
        return
    url_obj = urlopen(GET_PIP_URL)
    with open(DMG_PKG_DIR + '/get-pip.py', 'wt') as fobj:
        fobj.write(url_obj.read())


def get_wheels(version, requirements, pip_params):
    pip_exe = '{0}/{1}/bin/pip{1}'.format(PY_ORG_BASE, version, version)
    if not exists(pip_exe):
        raise RuntimeError('Need to install pip for python at ' +
                           '{0}/bin/python{1}'.format(PY_ORG_BASE, version))
    # Install wheel locally just in case
    check_call([pip_exe, 'install'] + pip_params + ['wheel'])
    check_call([pip_exe, 'wheel', '-w', DMG_PKG_DIR] + pip_params +
               list(requirements))


def write_post(py_version, requirements):
    to_install = ', '.join(['"{0}"'.format(r) for r in requirements])
    with open('scripts/postinstall', 'wt') as fobj:
        fobj.write(
r"""#!/usr/bin/env python
# Install into Python.org python
import sys
import os
from os.path import exists, dirname
from subprocess import check_call

# Find disk image files
package_path = os.environ.get('PACKAGE_PATH')
if package_path is None:
    sys.exit(10)
package_dir = dirname(package_path)
wheelhouse = package_dir + '/{pkg_dir}'
# Find Python.org Python
python_bin = '{py_org_base}/{py_version}/bin'
python_path = python_bin +  '/python{py_version}'
if not exists(python_path):
    sys.exit(20)
# Install pip
check_call([python_path, wheelhouse + '/get-pip.py', '-f', wheelhouse,
            '--no-setuptools'])
# Find pip
expected_pip = python_bin + '/pip{py_version}'
if not exists(expected_pip):
    sys.exit(30)
pip_cmd = [expected_pip, 'install', '--no-index', '--upgrade',
           '--find-links', wheelhouse]
check_call(pip_cmd + ['setuptools'])
check_call(pip_cmd + [{to_install}])
""".format(py_org_base = PY_ORG_BASE,
           py_version = py_version,
           to_install = to_install,
           pkg_dir = PKG_DIR,
          ))
    check_call(['chmod', 'a+x', 'scripts/postinstall'])


def write_pkg(identifier, version):
    pkg_fname = pjoin(DMG_DIR, '{0}-{1}.pkg'.format(identifier, version))
    check_call(['pkgbuild', '--root', 'pkg_template', '--nopayload', '--scripts',
                'scripts', '--identifier', identifier, '--version', version,
                pkg_fname])


def write_dmg(identifier, py_version, pkg_version):
    dmg_name = '{0}-py{1}-{2}'.format(
        identifier,
        py_version.replace('.', ''),
        pkg_version)
    check_call(['hdiutil', 'create', '-srcfolder', DMG_DIR,
                '-volname', dmg_name,
                dmg_name + '.dmg'])


def main():
    parser = ArgumentParser(description=DESCRIP,
                            epilog=EPILOG,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('pkg_name', type=str, help='root name of installer')
    parser.add_argument('pkg_version', type=str, help='version of installer')
    parser.add_argument('requirements', type=str, nargs='+',
                        help='pip requirement strings')
    parser.add_argument('--python-version',  type=str, default=PYTHON_VERSION,
                        help='Python version in major.minor format, e.g "3.4"')
    parser.add_argument('--no-index',  action='store_true',
                        help='disable search of pip indices when fetching '
                        'packages to make installer')
    parser.add_argument('--find-links', '-f', type=str, nargs='*', default=[],
                        help='locations to find packages to make installer')
    parser.add_argument('--get-pip-path', type=str,
                        help='local path to "get-pip.py"')
    # parse the command line
    args = parser.parse_args()
    pip_params = get_pip_params(args)
    mkdirs()
    get_pippers(pip_params, args.get_pip_path)
    get_wheels(args.python_version, args.requirements, pip_params)
    write_post(args.python_version, args.requirements)
    write_pkg(args.pkg_name, args.pkg_version)
    write_dmg(args.pkg_name, args.python_version, args.pkg_version)


if __name__ == '__main__':
    main()
