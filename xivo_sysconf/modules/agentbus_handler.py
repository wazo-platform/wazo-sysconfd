# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import logging
import re
import threading

from collections import namedtuple
from xivo_bus.resources.agent.event import DeleteAgentEvent, EditAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, DeleteQueueEvent, EditQueueEvent

logger = logging.getLogger(__name__)

AgentBusCommand = namedtuple('AgentBusCommand', ['module', 'action', 'id'])


class AgentBusHandler(object):

    _COMMAND_REGEX = re.compile(r'^(\w+)\.(\w+)\.(\d+)$')

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher
        self._lock = threading.Lock()

    def handle_command(self, command):
        bus_command = self._parse_command(command)
        if bus_command:
            self._execute_bus_command(bus_command)

    def _parse_command(self, command):
        match = self._COMMAND_REGEX.match(command)
        if not match:
            return None

        module, action, id_ = match.groups()

        return AgentBusCommand(module, action, id_)

    def _execute_bus_command(self, bus_command):
        client_action = (bus_command.module, bus_command.action)

        if client_action == ('agent', 'edit'):
            event = EditAgentEvent(bus_command.id)
        elif client_action == ('agent', 'delete'):
            event = DeleteAgentEvent(bus_command.id)
        elif client_action == ('queue', 'add'):
            event = CreateQueueEvent(bus_command.id)
        elif client_action == ('queue', 'edit'):
            event = EditQueueEvent(bus_command.id)
        elif client_action == ('queue', 'delete'):
            event = DeleteQueueEvent(bus_command.id)
        else:
            logger.warning('Unknown agent bus client action %s', client_action)
            return

        with self._lock:
            self._bus_publisher.publish(event)
