FROM debian:jessie
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    wget \
    git \
    apt-utils \
    python-pip \
    python-dev \
    python-dumbnet \
    python-netifaces \
    python-magic \
    python-m2crypto \
    libyaml-dev \
    ifupdown \
    sudo \
    curl \
    net-tools

# Install xivo-sysconfd
WORKDIR /usr/src
ADD . /usr/src/sysconfd
WORKDIR sysconfd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /etc/network/interfaces
RUN touch /var/log/xivo-sysconfd.log
RUN mkdir /etc/xivo/
RUN mkdir /var/run/xivo-sysconfd
RUN cp -a etc/xivo/* /etc/xivo/
WORKDIR /root

# Clean
RUN apt-get clean
RUN rm -rf /usr/src/*

EXPOSE 8668

CMD xivo-sysconfd -l debug -f
