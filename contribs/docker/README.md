Dockerfile for XiVO sysconfd

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t wazo-sysconfd github.com/wazo-platform/wazo-sysconfd.git

Or directly in the sources in contribs/docker

    docker build -t wazo-sysconfd .
  
## Usage

To run the container, do the following:

    docker run -d -p 8668:8668 -v /conf/sysconfd:/etc/xivo/sysconfd -t wazo-sysconfd

On interactive mode :

    docker run -p 8668:8668 -v /conf/sysconfd:/etc/xivo/sysconfd -it wazo-sysconfd bash

After launch wazo-sysconfd.

    wazo-sysconfd -d -f

## Infos

- Using docker version 1.5.0 (from get.docker.io) on ubuntu 14.04.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'
