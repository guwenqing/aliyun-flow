import base64
import json
import logging
import os

from my import flow
from my import gitee

next_pipeline_webhook = os.environ["NEXT_PIPELINE_WEBHOOK"]

logging.basicConfig(level=logging.DEBUG)

pr = gitee.parse_gitee_webhook_entry("pull_request")

if pr is None:
    logging.info("Not triggered by PR, skip the execution")
elif pr["updated_by"]["user_name"] == "zkfc-ci" or pr["updated_by"]["user_name"] == "Gitee":
    logging.info("Not triggered by user, skip the execution")
else:
    logging.info("Everything is good, continue the execution")
    b64 = base64.b64encode(json.dumps(pr).encode('utf-8')).decode('utf-8')
    logging.debug("Encoded base64:\n%s" % b64)
    flow.trigger_pipeline(next_pipeline_webhook, {"pull_request_base64": b64})
