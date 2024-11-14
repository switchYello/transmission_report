FROM python:3.9.20-alpine3.20

COPY src/base_config       /src/base_config
COPY src/core              /src/core
COPY src/start.sh          /src


ENV _RUN_IN_DOCKER='true'


# 安装依赖,增加执行权限
RUN pip3 install --no-cache-dir requests==2.31.0 tldextract==2.2.2 prettytable==3.11.0 \
    && chmod 755 /src/start.sh \
    && chmod 775 /src/base_config


WORKDIR /src
ENTRYPOINT ["sh", "/src/start.sh"]
CMD ["-?"]
