# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from xivo_bus.resources.agent.event import DeleteAgentEvent, EditAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, DeleteQueueEvent, EditQueueEvent
from wazo_sysconf.request_handlers.command import Command


class AgentdCommandFactory(object):

    _REGEX = re.compile(r'^(\w+\.\w+)\.(\d+)$')
    _ACTION_MAP = {
        'agent.edit': EditAgentEvent,
        'agent.delete': DeleteAgentEvent,
        'queue.add': CreateQueueEvent,
        'queue.edit': EditQueueEvent,
        'queue.delete': DeleteQueueEvent,
    }

    def __init__(self, agent_command_executor):
        self._executor = agent_command_executor

    def new_command(self, value):
        action, id_ = self._extract_action_and_id(value)
        event = self._new_event(action, id_)
        return Command(value, self._executor, event)

    def _extract_action_and_id(self, value):
        match = self._REGEX.match(value)
        if not match:
            raise ValueError('could not extract action and ID')

        return match.groups()

    def _new_event(self, action, id_):
        event_class = self._ACTION_MAP.get(action)
        if event_class is None:
            raise ValueError('unsupported action')

        return event_class(id_)


class AgentdCommandExecutor(object):

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher

    def execute(self, event):
        self._bus_publisher.publish(event)
