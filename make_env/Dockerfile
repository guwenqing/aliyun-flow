FROM registry.cn-beijing.aliyuncs.com/rdc-builds/base:1.0

RUN apt update
RUN apt install -y git make jq ssh

COPY .step/*.sh /root/
COPY make_env/*.sh /root/
COPY make_env/*.py /root/

RUN chmod +x /root/*.sh
RUN mkdir -p /root/.ssh && ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts && ssh-keyscan -t rsa gitee.com >> ~/.ssh/known_hosts

ENTRYPOINT [ "/root/entry.sh"]
