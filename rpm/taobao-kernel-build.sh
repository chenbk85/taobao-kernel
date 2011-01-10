#!/bin/bash
##for check
cd $1
python ./scripts/package.py
cd taobao-kernel-build
rpmbuild -bb  --rmsource *.spec --with baseonly --without fips --without kabichk --define="_rpmdir $1/taobao-kernel-build/rpm" --define="_builddir $1/taobao-kernel-build" --define="_sourcedir $1/taobao-kernel-build" --define="_tmppath $1/taobao-kernel-build/rpm"

