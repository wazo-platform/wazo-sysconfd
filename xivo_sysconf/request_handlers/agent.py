# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import re

from xivo_bus.resources.agent.event import DeleteAgentEvent, EditAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, DeleteQueueEvent, EditQueueEvent
from xivo_sysconf.request_handlers.command import Command


class AgentCommandFactory(object):

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


class AgentCommandExecutor(object):

    name = 'agentbus'

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher

    def execute(self, event):
        self._bus_publisher.publish(event)
