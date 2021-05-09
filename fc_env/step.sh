#!/bin/bash
set -e 

# 系统提供参数，从流水线上下文获取
echo [INFO] PIPELINE_ID=$PIPELINE_ID       # 流水线ID
echo [INFO] PIPELINE_NAME=$PIPELINE_NAME   # 流水线名称
echo [INFO] BUILD_NUMBER=$BUILD_NUMBER     # 流水线运行实例编号
echo [INFO] EMPLOYEE_ID=$EMPLOYEE_ID       # 触发流水线用户ID
echo [INFO] WORK_SPACE=$WORK_SPACE         # /root/workspace容器中目录
echo [INFO] PROJECT_DIR=$PROJECT_DIR       # 代码库根路径，默认为/root/workspace/code
echo [INFO] PLUGIN_DIR=$PLUGIN_DIR         # 插件路径，默认为/root/workspace/plugins
echo [INFO] BUILD_JOB_ID=$BUILD_JOB_ID     # build-service 任务ID

cd $PROJECT_DIR

# Write SSH private key
python3 /root/prepare-credential.py
bash -ex $WORK_SPACE/user_command.sh         # 执行 command 脚本