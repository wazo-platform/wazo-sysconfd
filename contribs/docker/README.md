Dockerfile for XiVO sysconfd

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t xivo-sysconfd github.com/xivo-pbx/xivo-sysconfd.git

Or directly in the sources in contribs/docker

    docker build -t xivo-sysconfd .
  
## Usage

To run the container, do the following:

    docker run -d -p 8668:8668 -v /conf/sysconfd:/etc/xivo/sysconfd -t xivo-sysconfd

On interactive mode :

    docker run -p 8668:8668 -v /conf/sysconfd:/etc/xivo/sysconfd -it xivo-sysconfd bash

After launch xivo-sysconfd.

    xivo-sysconfd -l debug -f

## Infos

- Using docker version 1.5.0 (from get.docker.io) on ubuntu 14.04.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'
