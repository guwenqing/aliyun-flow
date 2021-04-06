#!/bin/bash

docker build . -t registry.cn-hangzhou.aliyuncs.com/fc-public/fix-oss-ram:2.879
docker push registry.cn-hangzhou.aliyuncs.com/fc-public/fix-oss-ram:2.879