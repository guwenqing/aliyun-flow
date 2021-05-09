import json
import logging

import requests
from aliyunsdkdevops_rdc.request.v20200303.GetPipelineInstanceBuildNumberStatusRequest import \
    GetPipelineInstanceBuildNumberStatusRequest


def get_main_stage(clt, build_number, org_id, pipeline_id):
    request = GetPipelineInstanceBuildNumberStatusRequest()
    request.set_BuildNum(build_number)
    request.set_OrgId(org_id)
    request.set_PipelineId(pipeline_id)
    resp_str = clt.do_action_with_exception(request)
    resp = json.loads(resp_str.decode("utf-8"))

    for group in resp["Object"]["Groups"]:
        for stage in group["Stages"]:
            for comp in stage["Components"]:
                if comp["Name"] == "Main":
                    return stage

    return None


def analyze_main_stage(ms):
    if ms["Status"] != "FINISH":
        return ms["Status"]

    ret = "SUCCESS"
    for comp in ms["Components"]:
        if comp["Status"] == "FAIL":
            ret = "FAIL"
            break

    return ret


def make_pipeline_url(pipeline_id, build_number):
    return "https://flow.aliyun.com/pipelines/%s/builds/%s" % (pipeline_id, build_number)


def trigger_pipeline(webhook_url, payload):
    logging.info("Reset test: %s" % webhook_url)
    resp = requests.post(webhook_url, json=payload)

    logging.info("Status code: %d" % resp.status_code)
