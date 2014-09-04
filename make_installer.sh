PIP_TAG=1.5.6
PIP_URL=/Users/mb312/dev_trees/pip
TO_INSTALL="numpy scipy matplotlib"
mkdir pip wheels scripts pkg_template
pushd $PIP_URL && git archive $PIP_TAG | (cd $OLDPWD/pip && tar xf -) && popd
pip wheel -w wheels $TO_INSTALL
cat << EOF > scripts/postinstall
#!/usr/bin/env python
import sys
with open('/Users/mb312/which_python', 'wt') as fobj:
    fobj.write(sys.prefix + '\n')
EOF
chmod u+x scripts/postinstall
pkgbuild --root pkg_template --nopayload --scripts scripts --identifier scipy-stack scipy-stack.pkg
