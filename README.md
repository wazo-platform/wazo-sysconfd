# wazo-sysconfd

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-sysconfd)](https://jenkins.wazo.community/job/wazo-sysconfd)

wazo-sysconfd is a daemon for configuring system parameters on a Wazo server
It is used to execute command requiring special privilege of a system (ex: root, asterisk). It shims
Wazo and the installed host together. It usages is mandatory for a traditional installation of Wazo,
but *should* be not necessary for container installations

## Running unit tests

```shell
tox --recreate -e py37
```

## Running integration tests

```shell
tox --recreate -e integration
```

## Development

### Request handlers architecture

![Architecture diagram](doc/wazo-sysconfd-request-handlers-architecture.svg)
[Architecture diagram source](https://excalidraw.com/#json=5720016209051648,87-AW9gy4HNCa4M0pwUi6w)
