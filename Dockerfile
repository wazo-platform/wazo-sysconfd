## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    wget \
    apt-utils \
    python-pip \
    python-dev \
    libyaml-dev \
    python-dumbnet \
    python-netifaces \
    python-magic \
    python-m2crypto \
    ifupdown \
    sudo \
    curl \
    net-tools

# Install xivo-sysconfd
WORKDIR /usr/src
RUN . /usr/src/sysconfd
WORKDIR sysconfd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /etc/network/interfaces
RUN touch /var/log/xivo-sysconfd.log
RUN mkdir -p /etc/xivo/xivo-sysconfd
RUN mkdir /var/run/xivo-sysconfd
RUN cp -a etc/xivo/xivo-sysconfd/xivo-sysconfd.yml /etc/xivo/xivo-sysconfd/
WORKDIR /root

# Clean
RUN apt-get clean
RUN rm -rf /usrc/src/*

EXPOSE 8668

CMD xivo-sysconfd -l debug -f
