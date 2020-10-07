xivo-sysconfd
=========
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-sysconfd)](https://jenkins.wazo.community/job/xivo-sysconfd)

xivo-sysconfd is a daemon for configuring system parameters on a Wazo server.


Running unit tests
------------------

```
apt-get install python-dev libyaml-dev
pip install tox
tox --recreate -e py27
```
