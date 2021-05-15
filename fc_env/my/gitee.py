import base64
import json
import logging
import os
import re

import requests


def parse_gitee_webhook_entry(key):
    key_b64 = "%s_base64" % key

    if key not in os.environ and key_b64 not in os.environ:
        return None

    ret = {}

    if key_b64 in os.environ:
        base64_str = os.environ[key_b64] + "=="
        value_to_parse = base64.b64decode(base64_str.encode('utf-8')).decode('utf-8')
    else:
        value_to_parse = os.environ[key]

        if "title" in os.environ:
            value_to_parse = value_to_parse.replace("title=%s, " % os.environ["title"], "")
            ret["title"] = os.environ["title"]

        if "body" in os.environ:
            value_to_parse = value_to_parse.replace("body=%s, " % os.environ["body"], "")
            ret["body"] = os.environ["body"]

        value_to_parse = re.sub(pattern=r'([a-z0-9A-Z]+=, )', repl=r'', string=value_to_parse)
        value_to_parse = value_to_parse.replace(", ", ",")
        value_to_parse = re.sub(pattern=r'([^=^{^}^[^\]^,^]+)', repl=r'"\1"', string=value_to_parse)
        value_to_parse = value_to_parse.replace("=", ":")

    logging.debug("Value before parsing = \n %s" % value_to_parse)

    obj = json.loads(value_to_parse)
    ret.update(obj)

    logging.debug("Value after parsing = \n %s" % json.dumps(ret))

    return ret


def match_entry(pull_request_obj, clone_url):
    obj = pull_request_obj["head"]["repo"]

    for key in obj:
        val = obj[key]
        if val == clone_url:
            return True

    return False


GITEE_PR_RESET_TEST = "https://gitee.com/api/v5/repos/%s/%s/pulls/%s/testers"
GITEE_PR_ACCEPT_TEST = "https://gitee.com/api/v5/repos/%s/%s/pulls/%s/test"
GITEE_PR_TEST_COMMENT = "https://gitee.com/api/v5/repos/%s/%s/pulls/%s/comments"


def pr_reset_test(pr, token):
    repo = pr["head"]["repo"]
    url = GITEE_PR_RESET_TEST % (repo["namespace"], repo["path"], pr["number"])
    request = {
        "access_token": token,
        "reset_all": "true"
    }
    logging.info("Reset test: %s" % url)
    resp = requests.patch(url, json=request)

    logging.info("Status code: %d" % resp.status_code)


def pr_accept_test(pr, token):
    pr_comment(pr, token, "Test is SUCCESSFUL, accept test!")

    repo = pr["head"]["repo"]
    url = GITEE_PR_ACCEPT_TEST % (repo["namespace"], repo["path"], pr["number"])
    request = {
        "access_token": token,
        "force": "true"
    }
    logging.info("Accept test: %s" % url)
    resp = requests.post(url, json=request)

    logging.info("Status code: %d" % resp.status_code)


def pr_comment(pr, token, comment):
    repo = pr["head"]["repo"]
    url = GITEE_PR_TEST_COMMENT % (repo["namespace"], repo["path"], pr["number"])
    request = {
        "access_token": token,
        "body": comment
    }
    logging.info("Add PR comment: %s" % url)
    resp = requests.post(url, json=request)

    logging.info("Status code: %d" % resp.status_code)
