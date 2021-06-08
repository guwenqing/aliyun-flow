import argparse
import logging
import os
import shutil
import tempfile


def my_system(command):
    logging.debug("Execute %s" % command)
    os.system(command)


def parse_args():
    parser = argparse.ArgumentParser(description='Replace plugin tool.')
    parser.add_argument('--source', help='Source to the replacement files', required=True)
    parser.add_argument('--target', help='Target path to update', required=True)
    args = parser.parse_args()

    return args


def replace_plugins(source_path, target_path):
    source = os.listdir(source_path)
    target = os.listdir(target_path)

    for source_item in source:
        logging.info("Find plugin to replace: %s" % source_item)
        found = None
        for candidate in target:
            if candidate.startswith(source_item) and candidate.endswith(".jar") and "nl_zh_" not in candidate:
                found = candidate
                break

        if found is None:
            logging.warning("Cannot find candidate to replace %s" % source_item)
            continue

        logging.info("Start replace jar %s" % found)

        dirpath = tempfile.mkdtemp()
        dirpath_inner = dirpath + "/inner"
        os.makedirs(dirpath_inner)

        my_system("cp '%s' '%s'" % (os.path.join(target_path, found), dirpath_inner))
        my_system("cd '%s' && jar xvf '%s' && rm -rf '%s'" % (dirpath_inner, found, found))
        my_system("cp -rf %s/* %s/" % (os.path.join(source_path, source_item), dirpath_inner))
        my_system("cd '%s' && jar cmf0 META-INF/MANIFEST.MF ../%s  ." % (dirpath_inner, found))

        my_system("cp -rf %s %s" % (os.path.join(dirpath, found), target_path))

        # ... do stuff with dirpath
        shutil.rmtree(dirpath)


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    replace_plugins(args.source, args.target)


if __name__ == "__main__":
    main()
