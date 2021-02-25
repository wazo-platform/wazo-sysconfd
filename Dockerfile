FROM python:2.7-slim-buster AS compile-image
MAINTAINER Wazo Maintainers <dev@wazo.community>

RUN apt-get -qq update && apt-get -qq -y install python-virtualenv
RUN virtualenv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /usr/local/src/wazo-sysconfd/requirements.txt
WORKDIR /usr/local/src/wazo-sysconfd
RUN pip install -r requirements.txt

COPY setup.py /usr/local/src/wazo-sysconfd/
COPY xivo_sysconf /usr/local/src/wazo-sysconfd/xivo_sysconf
COPY bin/xivo-sysconfd /usr/local/src/wazo-sysconfd/bin/
RUN python setup.py install

FROM python:2.7-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY etc/xivo /etc/xivo
COPY templates /usr/share/xivo-sysconfd/templates

RUN install -D -o root -g root /dev/null /etc/network/interfaces \
    && install -D -o root -g root /dev/null /var/log/xivo-sysconfd.log

EXPOSE 8668

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["xivo-sysconfd", "-l", "debug", "--listen-addr=0.0.0.0"]
