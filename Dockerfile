FROM python:3.9-slim-bullseye AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN apt-get -qq update && apt-get -qq -y install python3-virtualenv gcc
RUN python3 -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /usr/local/src/wazo-sysconfd/requirements.txt
WORKDIR /usr/local/src/wazo-sysconfd
RUN pip install -r requirements.txt

COPY setup.py /usr/local/src/wazo-sysconfd/
COPY wazo_sysconfd /usr/local/src/wazo-sysconfd/wazo_sysconfd
RUN python setup.py install

FROM python:3.9-slim-bullseye AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./etc/wazo-sysconfd /etc/wazo-sysconfd
COPY ./templates /usr/share/wazo-sysconfd/templates

RUN true\
    && mkdir -p /etc/wazo-sysconfd/conf.d \
    && mkdir -p /etc/xivo \
    && install -D -o root -g root /dev/null /etc/network/interfaces \
    && install -D -o root -g root /dev/null /var/log/wazo-sysconfd.log

EXPOSE 8668

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-sysconfd", "-l", "debug"]
