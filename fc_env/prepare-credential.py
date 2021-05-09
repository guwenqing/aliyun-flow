import json
import os

ID_RSA = "/root/.ssh/id_rsa"
NETRC = "/root/.netrc"


def write_ssh(pk):
    f = open(ID_RSA, "w")
    f.write(pk)
    f.close()

    os.chmod(ID_RSA, 0o400)


def write_netrc(usr, pwd):
    f = open(NETRC, "w")
    f.write("machine gitee.com login %s password %s\n" % (usr, pwd))
    f.close()

    os.chmod(NETRC, 0o400)


if "SOURCES" in os.environ:
    raw = os.environ["SOURCES"]
    data = json.loads(raw)
    if data and len(data) > 0:
        item = data[0]
        if "data" in item and "sshPrivateKey" in item["data"]:
            print("Find ssh key, write to $ID_RSA! \n")
            private_key = item["data"]["sshPrivateKey"]
            write_ssh(private_key)
        if "data" in item and "password" in item["data"]:
            print("Find http password, write to $NETRC! \n")
            password = item["data"]["password"]
            username = item["data"]["userName"]
            write_netrc(username, password)

if "GITEE_USERNAME" in os.environ and "GITEE_TOKEN" in os.environ:
    print("Find env variable for GITEE")
    write_netrc(os.environ["GITEE_USERNAME"], os.environ["GITEE_TOKEN"])
