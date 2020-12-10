#!/bin/bash

region_name=`curl -s --connect-timeout 3 --max-time 1 --retry-delay 1 --retry 3 http://100.100.100.200/latest/meta-data/region-id`
if [ "$?" == "0" ] && [ "$region_name" = "cn-beijing" ]; then
  echo oss-cn-beijing-internal.aliyuncs.com
else
  echo oss-cn-beijing.aliyuncs.com
fi
