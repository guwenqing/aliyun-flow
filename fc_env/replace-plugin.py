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
        if source_item.startswith("."):
            continue

        logging.info("Find plugin to replace: %s" % source_item)
        found_jar_list = []
        found_dir_list = []

        for candidate in target:
            if candidate.startswith(source_item + "_"):
                if candidate.endswith(".jar"):
                    found_jar_list.append(candidate)
                else:
                    found_dir_list.append(candidate)

        if len(found_jar_list) == 0 and len(found_dir_list) == 0:
            logging.warning("Cannot find candidate to replace %s" % source_item)
            continue

        if len(found_jar_list) + len(found_dir_list) != 1:
            logging.warning("Multiple entries found for %s" % source_item)
            continue

        for found in found_jar_list:
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

        for found in found_dir_list:
            my_system("cp -rf %s/* %s/" % (os.path.join(source_path, source_item), os.path.join(target_path, found)))


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    replace_plugins(args.source, args.target)


if __name__ == "__main__":
    main()
