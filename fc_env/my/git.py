import logging
import os
import re
import subprocess
import tempfile

import yaml
import yamlordereddictloader

from . import gitee


def _run_command(command):
    logging.debug("Execute: %s" % command)
    result = os.system(command)

    return result


def _run_command_with_output(command):
    logging.debug("Execute: %s" % command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    return result.stdout


def _get_folder_name(repo_url):
    sp = list(filter(lambda x: x.strip() != "", repo_url.split("/")))
    folder_name = re.sub("\\.git$", "", sp[-1])

    return folder_name


def _cleanup_target(clone_to, folder_name):
    if not os.path.exists(clone_to):
        _run_command("mkdir -p \"%s\"" % clone_to)
    else:
        if os.path.exists(clone_to + "/" + folder_name):
            _run_command("cd \"%s\" && rm -rf \"%s\"" % (clone_to, folder_name))


def do_git_clone(repo_url, clone_to, folder_name):
    logging.debug("Git clone %s: %s" % (repo_url, clone_to))

    if folder_name is None:
        folder_name = _get_folder_name(repo_url)
    _cleanup_target(clone_to, folder_name)

    ret = _run_command("cd \"%s\" && git clone \"%s\" \"%s\"" % (clone_to, repo_url, folder_name))
    if ret != 0:
        raise Exception("Git clone failed!!")
    return clone_to + "/" + folder_name


def do_git_clone_with_smart_detection(repo_url, clone_to, folder_name, pr):
    main_repo_path = do_git_clone(repo_url, clone_to, folder_name)

    if pr is not None:
        is_matched = gitee.match_entry(pr, repo_url)
        logging.info("Detected PR info! PR matches to %s: %s" % (repo_url, str(is_matched)))

        if is_matched:
            logging.info("Checkout to sha %s" % pr["head"]["sha"])
            do_git_checkout(main_repo_path, pr["head"]["sha"])

    sha1 = do_get_sha1(main_repo_path)

    return main_repo_path, sha1


def do_git_checkout(path, sha):
    logging.debug("Git checkout %s: %s" % (path, sha))

    ret = _run_command("cd \"%s\" && git checkout \"%s\"" % (path, sha))
    if ret != 0:
        raise Exception("Git checkout failed!!")


def do_get_sha1(path):
    logging.debug("Git get SHA1 %s" % path)
    res = _run_command_with_output("cd \"%s\" && git rev-parse HEAD" % path)
    return res.decode('UTF-8').strip()


def get_baseline(path, baseline_file="baseline.yaml"):
    absolute_path = os.path.abspath(path + "/" + baseline_file)
    if os.path.exists(absolute_path):
        data = yaml.load(open(absolute_path), Loader=yamlordereddictloader.Loader)
        return data

    return None


def write_baseline(path, baseline, baseline_file="baseline.yaml"):
    absolute_path = os.path.abspath(path + "/" + baseline_file)
    yaml.dump(
        baseline,
        open(absolute_path, 'w'),
        Dumper=yamlordereddictloader.Dumper,
        default_flow_style=False)


def clone_main_repo(repo_url, clone_to, folder_name, pr):
    main_repo_path, sha1 = do_git_clone_with_smart_detection(repo_url, clone_to, folder_name, pr)
    logging.info("Main repo is cloned to: %s" % main_repo_path)

    baseline = get_baseline(main_repo_path)

    if baseline is not None:
        baseline["main"] = {
            "repo": repo_url,
            "sha1": sha1
        }

    return main_repo_path, baseline


def _copy_repo(source_path, clone_to, exploded):
    command = "cd \"%s\" && cp -rf \"%s\" ." % (clone_to, source_path)

    if exploded:
        command = "cd \"%s\" && cp -rf %s/* ." % (clone_to, source_path)

    logging.debug("Execute copy: %s" % command)

    _run_command(command)


def setup_modules(main_repo_path, baseline, pr):
    temp_dir = tempfile.mkdtemp(prefix="git-")

    for repo_obj in baseline["repos"]:
        if "sha1" not in repo_obj:
            repo_obj["sha1"] = "master"

        if "explode" not in repo_obj:
            repo_obj["explode"] = False

        temp_repo_path, sha1 = do_git_clone_with_smart_detection(repo_obj["repo"], temp_dir, None, pr)
        repo_obj["sha1"] = sha1

        clone_to = main_repo_path + "/" + repo_obj["clone_to"]

        if not repo_obj["explode"]:
            folder_name = _get_folder_name(repo_obj["repo"])
            _cleanup_target(clone_to, folder_name)

        _copy_repo(temp_repo_path, clone_to, repo_obj["explode"])
