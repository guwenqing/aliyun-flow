import os
import shutil
import tempfile

PLUGIN_REPLACE_SOURCE = "/Users/wgu/Desktop/plugin_modify"
PLUGIN_REPOSITORY = "/Users/wgu/projects/mdt/org.fc.mdt.build/products/org.fc.mdt.products.desktop/target/products/metagraph.desktop/win32/win32/x86_64/plugins"
PLUGIN_OUTPUT_TARGET = ["/Users/wgu/Desktop/plugin_modify_output"]

for output in PLUGIN_OUTPUT_TARGET:
    if not os.path.exists(output):
        os.makedirs(output)

source = os.listdir(PLUGIN_REPLACE_SOURCE)
target = os.listdir(PLUGIN_REPOSITORY)

def my_system(command):
    print("Execute %s" % command)
    os.system(command)


for source_item in source:
    found = None
    for candidate in target:
        if candidate.startswith(source_item) and candidate.endswith(".jar"):
            found = candidate
            break

    if found is None:
        print("ERROR: %s cannot find candidate to replace" % source_item)
        continue

    dirpath = tempfile.mkdtemp()
    dirpath_inner = dirpath + "/inner"
    os.makedirs(dirpath_inner)

    my_system("cp '%s' '%s'" % (PLUGIN_REPOSITORY + "/" + found, dirpath_inner))
    my_system("cd '%s' && jar xvf '%s' && rm -rf '%s'" % (dirpath_inner, found, found))
    my_system("cp -rf %s/* %s/" % (PLUGIN_REPLACE_SOURCE + "/" + source_item, dirpath_inner))
    my_system("cd '%s' && jar cmf0 META-INF/MANIFEST.MF ../%s  ." % (dirpath_inner, found))

    for output in PLUGIN_OUTPUT_TARGET:
        my_system("cp %s %s" % (dirpath + "/" + found, output))

    # ... do stuff with dirpath
    shutil.rmtree(dirpath)

