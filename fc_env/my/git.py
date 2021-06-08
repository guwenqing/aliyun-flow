import logging
import os
import re
import subprocess
import tempfile
import time

import psutil
import yaml
import yamlordereddictloader

from . import gitee


def __kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def __run_command(command, timeout=None):
    logging.debug("Execute: %s" % command)
    p = subprocess.Popen(['/bin/sh', '-c', '%s' % command])
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        os.system("ps ux")
        logging.error("Timed out and kill the process.")
        __kill(p.pid)
        os.system("ps ux")

    return p.returncode


def __run_command_with_output(command):
    logging.debug("Execute: %s" % command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    return result.stdout.decode("utf-8").strip()


def __get_folder_name(repo_url):
    sp = list(filter(lambda x: x.strip() != "", repo_url.split("/")))
    folder_name = re.sub("\\.git$", "", sp[-1])

    return folder_name


def git_clone_or_update(repo_url, clone_to, folder_name, retry_times=10):
    if folder_name is None:
        folder_name = __get_folder_name(repo_url)

    while retry_times > 0:
        retry_times = retry_times - 1
        try:
            return __do_git_clone_or_update(repo_url, clone_to, folder_name)
        except Exception as e:
            logging.info("%s\nGit clone or update failed retry..." % str(e))
            if retry_times > 0:
                time.sleep(15)
                target_path_full = os.path.join(clone_to, folder_name)
                __run_command("rm -rf \"%s\"" % target_path_full)
            else:
                logging.error("Operation failed after retrying!")
                raise e


def __do_git_clone_or_update(repo_url, clone_to, folder_name):
    logging.debug("Git clone %s: %s" % (repo_url, clone_to))

    target_path_full = os.path.join(clone_to, folder_name)

    # Not completed git clone operation will affect the overall
    if os.path.exists(target_path_full):
        git_check_path = __run_command_with_output("cd \"%s\" && git rev-parse --show-toplevel" % target_path_full)
        target_path_full_absolute = os.path.abspath(target_path_full.strip())
        if git_check_path != target_path_full_absolute:
            raise Exception("Current path %s does not have correct git cloned, will be deleted." % target_path_full)

    if os.path.exists(target_path_full):
        logging.info("Clone path %s existed, try to update..." % target_path_full)
        ret = __run_command(("cd \"%s\" && git fetch && git clean -xfd && " +
                             "git reset HEAD --hard && git checkout master && git reset origin/master --hard")
                            % target_path_full)
    else:
        ret = __run_command("cd \"%s\" && git clone \"%s\" \"%s\"" % (clone_to, repo_url, folder_name), 600)
    if ret != 0:
        raise Exception("Git clone/update failed!!")
    return target_path_full


def prepare_git_with_detection(repo_url, clone_to, folder_name, pr, sha=None):
    repo_path = git_clone_or_update(repo_url, clone_to, folder_name)

    if pr is not None:
        is_matched = gitee.match_entry(pr, repo_url)
        logging.info("Detected PR info! PR matches to %s: %s" % (repo_url, str(is_matched)))

        if is_matched:
            logging.info("Checkout to sha %s" % pr["head"]["sha"])
            do_git_checkout(repo_path, pr["head"]["sha"])

    elif sha is not None:
        do_git_checkout(repo_path, sha)

    setup_file_path = os.path.join(repo_path, "setup.sh")
    if os.path.exists(setup_file_path):
        ret = __run_command("cd \"%s\" && ./setup.sh" % repo_path)
        if ret != 0:
            logging.warning("Setup file failed to execute! Please check!")

    sha1 = do_get_sha1(repo_path)

    return repo_path, sha1


def do_git_checkout(path, sha):
    logging.debug("Git checkout %s: %s" % (path, sha))

    ret = __run_command("cd \"%s\" && git checkout \"%s\"" % (path, sha))
    if ret != 0:
        raise Exception("Git checkout failed!!")


def do_get_sha1(path):
    logging.debug("Git get SHA1 %s" % path)
    return __run_command_with_output("cd \"%s\" && git rev-parse HEAD" % path)


def get_baseline(path, baseline_file="baseline.yaml"):
    absolute_path = os.path.abspath(os.path.join(path, baseline_file))
    if os.path.exists(absolute_path):
        data = yaml.load(open(absolute_path), Loader=yamlordereddictloader.Loader)
        return data

    return None


def write_baseline(path, baseline, baseline_file="baseline.yaml"):
    absolute_path = os.path.abspath(os.path.join(path, baseline_file))
    yaml.dump(
        baseline,
        open(absolute_path, 'w'),
        Dumper=yamlordereddictloader.Dumper,
        default_flow_style=False)


def clone_main_repo(repo_url, clone_to, folder_name, pr):
    main_repo_path, sha1 = prepare_git_with_detection(repo_url, clone_to, folder_name, pr)
    logging.info("Main repo is cloned to: %s" % main_repo_path)

    baseline = get_baseline(main_repo_path)

    if baseline is not None:
        baseline["main"] = {
            "repo": repo_url,
            "sha1": sha1
        }

    return main_repo_path, baseline


def explode_repo(source_path, clone_to):
    for d in os.listdir(source_path):
        if d.startswith("."):
            continue
        full_source_path = os.path.join(source_path, d)
        full_dest_path = os.path.join(clone_to, d)
        command = "rm -rf \"%s\" && cp -rf \"%s\" \"%s\"" % (full_dest_path, full_source_path, full_dest_path)
        __run_command(command)


def setup_modules(main_repo_path, baseline, pr):
    temp_dir = tempfile.mkdtemp(prefix="git-")

    for repo_obj in baseline["repos"]:
        if "explode" not in repo_obj:
            repo_obj["explode"] = False

        clone_to = os.path.join(main_repo_path, repo_obj["clone_to"])
        sha1 = None

        if "sha1" in repo_obj and repo_obj["sha1"] is not None:
            sha1 = repo_obj["sha1"]

        target_clone = temp_dir
        if not repo_obj["explode"]:
            target_clone = clone_to

        temp_repo_path, sha1 = prepare_git_with_detection(repo_obj["repo"], target_clone, None, pr, sha1)
        repo_obj["sha1"] = sha1

        if repo_obj["explode"]:
            explode_repo(temp_repo_path, clone_to)
