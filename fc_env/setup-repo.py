import argparse
import logging
import os
import re
import shutil

from my import gitee


def parse_args():
    parser = argparse.ArgumentParser(description='Setup-repo tool.')
    parser.add_argument('--repo', help='URL to the repo', required=True)
    parser.add_argument('--target', help='Target path', default=".")
    args = parser.parse_args()

    return args


def _do_git_clone(repo_url, target_path):
    logging.debug("Git clone %s: %s" % (repo_url, target_path))

    sp = list(filter(lambda x: x.strip() != "", repo_url.split("/")))
    folder_name = re.sub("\\.git$", '', sp[-1])

    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

    ret = os.system("cd '%s' && git clone '%s' %s && cd --" % (target_path, repo_url, folder_name))
    if ret != 0:
        raise Exception("Git clone failed!!")
    return target_path + "/" + folder_name


def _do_git_checkout(path, sha):
    logging.debug("Git checkout %s: %s" % (path, sha))

    ret = os.system("cd '%s' && git checkout '%s' && cd --" % (path, sha))
    if ret != 0:
        raise Exception("Git checkout failed!!")


# only consider before merge case
def clone_main_repo(repo_url, target_path):
    main_repo_path = _do_git_clone(repo_url, target_path)
    logging.info("Main repo is cloned to: %s" % main_repo_path)

    pr = gitee.parse_gitee_webhook_entry("pull_request")
    if pr is not None:
        is_matched = gitee.match_entry(pr, repo_url)
        logging.info("Detected PR info! PR matches to %s: %s" % (repo_url, str(is_matched)))

        if is_matched:
            logging.info("Checkout to sha %s" % pr["head"]["sha"])
            _do_git_checkout(main_repo_path, pr["head"]["sha"])

    return main_repo_path


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    main_repo_path = clone_main_repo(args.repo, args.target)


if __name__ == "__main__":
    main()
