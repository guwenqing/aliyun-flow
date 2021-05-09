import logging
import os
import time
from aliyunsdkcore.client import AcsClient

from my import flow
from my import gitee

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
gitee_token = os.environ["GITEE_TOKEN"]
pipeline_url = flow.make_pipeline_url(pipeline_id, build_number)

logging.basicConfig(level=logging.DEBUG)

pr = gitee.parse_gitee_webhook_entry("pull_request")

if pr is not None:
    gitee.pr_comment(pr, gitee_token, "Test is started! URL: %s" % pipeline_url)
    gitee.pr_reset_test(pr, gitee_token)

while True:
    ms = flow.get_main_stage(client, build_number, org_id, pipeline_id)

    if ms is None:
        logging.error("Cannot find Main stage to monitor, please make sure the main stage is named as Main")
        exit(1)

    status = flow.analyze_main_stage(ms)

    if status != "SUCCESS" and status != "FAIL":
        logging.info("Main stage is still running: %s" % status)
        time.sleep(5)
    else:
        logging.info("Main stage is %s" % status)

        if pr is not None:
            if status == "SUCCESS":
                gitee.pr_accept_test(pr, gitee_token)
            else:
                gitee.pr_comment(pr, gitee_token, "Test is not successful!")
        break
