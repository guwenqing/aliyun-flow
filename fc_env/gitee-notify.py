import os
import logging
import time
import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkdevops_rdc.request.v20200303.GetPipelineInstanceBuildNumberStatusRequest import \
    GetPipelineInstanceBuildNumberStatusRequest

ALIYUN_LOC = "cn-beijing"
ALIYUN_PK = os.environ["ALIYUN_AK"]
ALIYUN_TOKEN = os.environ["ALIYUN_TOKEN"]

client = AcsClient(
    ALIYUN_PK,
    ALIYUN_TOKEN,
    ALIYUN_LOC
)

client.add_endpoint("cn-beijing", "devops-rdc", "api-devops.cn-beijing.aliyuncs.com")

pipeline_id = os.environ["PIPELINE_ID"]
build_number = os.environ["BUILD_NUMBER"]
org_id = os.environ["ENGINE_GLOBAL_PARAM_ORGANIZATION_ID"]
logging.basicConfig(level=logging.DEBUG)


def get_main_stage(clt):
    request = GetPipelineInstanceBuildNumberStatusRequest()
    request.set_BuildNum(build_number)
    request.set_OrgId(org_id)
    request.set_PipelineId(pipeline_id)
    resp_str = clt.do_action_with_exception(request)
    resp = json.loads(resp_str)

    for group in resp["Object"]["Groups"]:
        for stage in group["Stages"]:
            for comp in stage["Components"]:
                if comp["Name"] == "Main":
                    return stage

    return None


while True:
    ms = get_main_stage(client)

    if ms is None:
        logging.error("Cannot find Main stage to monitor, please make sure the main stage is named as Main")
        exit(1)

    if ms["Status"] == "FINISH":
        break

    logging.info("Main stage is still running: %s" % ms.status)
    time.sleep(5000)

pipeline_status = "SUCCESS"
for comp in ms["Components"]:
    if comp == "FAIL":
        pipeline_status = "FAIL"
        break

logging.info("Main stage is %s" % pipeline_status)
