FROM registry.cn-beijing.aliyuncs.com/rdc-builds/base:1.0

RUN apt update
RUN apt install -y git make jq ssh
RUN mkdir -p /root/.ssh && ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts && ssh-keyscan -t rsa gitee.com >> ~/.ssh/known_hosts

WORKDIR /root
COPY .step/*.sh /root/
COPY fc_env/*.sh /root/
COPY fc_env/*.py /root/
COPY fc_env/my /root/my

RUN chmod +x /root/*.sh

ENTRYPOINT [ "/root/entry.sh"]
