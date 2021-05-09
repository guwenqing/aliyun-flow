import json
import logging
import os
import re


def parse_gitee_webhook_entry(key):
    if key not in os.environ:
        return None

    value_to_parse = os.environ[key]
    ret = {}

    if "title" in os.environ:
        value_to_parse = value_to_parse.replace("title=%s, " % os.environ["title"], "")
        ret["title"] = os.environ["title"]

    if "body" in os.environ:
        value_to_parse = value_to_parse.replace("body=%s, " % os.environ["body"], "")
        ret["body"] = os.environ["body"]

    value_to_parse = value_to_parse.replace("description=, ", "")

    value_to_parse = re.sub(pattern=r'([^=^{^}^[^\]^,^ ]+)', repl=r'"\1"', string=value_to_parse)
    value_to_parse = value_to_parse.replace("=", ":")

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
