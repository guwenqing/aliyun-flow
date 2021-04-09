import json
import os

ID_RSA = "/root/.ssh/id_rsa"
NETRC = "/root/.netrc"

if "SOURCES" in os.environ:
    raw = os.environ["SOURCES"]
    data = json.loads(raw)
    if data and len(data) > 0:
        item = data[0]
        if "data" in item and "sshPrivateKey" in item["data"]:
            print("Find ssh key, write to $ID_RSA! \n")
            private_key = item["data"]["sshPrivateKey"]
            f = open(ID_RSA, "w")
            f.write(private_key)
            f.close()

            os.chmod(ID_RSA, 0o400)
        if "data" in item and "password" in item["data"]:
            print("Find http password, write to $NETRC! \n")
            password = item["data"]["password"]
            username = item["data"]["userName"]
            f = open(NETRC, "w")
            f.write("machine gitee.com login %s password %s\n" % (username, password))
            f.close()

            os.chmod(NETRC, 0o400)
