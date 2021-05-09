import logging

from my import git


def main():
    logging.basicConfig(level=logging.DEBUG)

    baseline = git.get_baseline(".")

    git.setup_modules(".", baseline, None)


if __name__ == "__main__":
    main()
