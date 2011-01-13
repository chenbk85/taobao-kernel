#!/bin/bash
##for check
sudo yum install perl-TimeDate -y
cd $1
python ./scripts/package.py
cd taobao-kernel-build
rpmbuild -bb  --rmsource *.spec --without debug --without fips --without kabichk --without perftool --without xen --define="_rpmdir $1/rpm" --define="_builddir $1/taobao-kernel-build" --define="_sourcedir $1/taobao-kernel-build" --define="_tmppath $1/rpm"
for mypk in `ls *.rpm`
do
	t_pk_l=${mypk//-/ }
	t_pk_array=($t_pk_l)
	ac=${#t_pk_array[*]}
	version=${t_pk_array[$ac-2]}
	echo $version > $1/rpm/$2-VER.txt
	break
done

