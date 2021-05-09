import argparse
import logging

from my import git
from my import gitee


def parse_args():
    parser = argparse.ArgumentParser(description='Setup-repo tool.')
    parser.add_argument('--repo', help='URL to the repo', required=True)
    parser.add_argument('--clone-to', dest="clone_to", help='Target path to clone to', default=".")
    parser.add_argument('--folder-name', dest="folder_name", help='Folder name of the clone', default='repo')
    args = parser.parse_args()

    return args


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()

    pr = gitee.parse_gitee_webhook_entry("pull_request")
    main_repo_path, baseline = git.clone_main_repo(args.repo, args.clone_to, args.folder_name, pr)

    if baseline is not None:
        git.setup_modules(main_repo_path, baseline, pr)
        git.write_baseline(main_repo_path, baseline)


if __name__ == "__main__":
    main()
