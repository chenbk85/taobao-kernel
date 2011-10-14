#!/bin/sh
cd $1/rpm
python taobao-kernel-buildqa.py $3 $4
for name in `ls *.rpm`
do 
  yum-upload $name  --osver $ABS_OS --arch ${plat} --group yum --batch
done
