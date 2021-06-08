FROM registry.cn-beijing.aliyuncs.com/rdc-builds/base:1.0

RUN apt update && apt install -y git make jq ssh python3 python3-pip curl openjdk-8-jdk zip
RUN mkdir -p /root/.ssh && ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts && ssh-keyscan -t rsa gitee.com >> ~/.ssh/known_hosts

WORKDIR /root
COPY .step/*.sh /root/
COPY fc_env/*.sh /root/
COPY fc_env/*.py /root/
COPY fc_env/my /root/my

RUN chmod +x /root/*.sh

COPY fc_env/requirements.txt /root/
RUN curl -fsSL -o- https://bootstrap.pypa.io/pip/3.5/get-pip.py | python3.5 && pip3 install -r requirements.txt

ENTRYPOINT [ "/root/entry.sh"]
