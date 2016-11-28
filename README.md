xivo-sysconfd
=========
[![Build Status](https://travis-ci.org/wazo-pbx/xivo-sysconfd.png?branch=master)](https://travis-ci.org/wazo-pbx/xivo-sysconfd)

xivo-sysconfd is a daemon for configuring system parameters on a XiVO server


Running unit tests
------------------

```
apt-get install python-dev libyaml-dev
pip install tox
tox --recreate -e py27
```
