"""
pythoneda/artifact/nix_flake/infrastructure/dbus/git_dbus_signal_emitter.py

This file defines the NixFlakeDbusSignalEmitter class.

Copyright (C) 2023-today rydnr's pythoneda-artifact/nix-flake-infrastructure

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from dbus_next import BusType
from pythoneda.infrastructure.dbus import DbusSignalEmitter
from pythoneda.shared.artifact.events.code import (
    ChangeStagingCodeExecutionPackaged,
    ChangeStagingCodePackaged,
)
from pythoneda.shared.artifact.events.code.infrastructure.dbus import (
    DbusChangeStagingCodeExecutionPackaged,
    DbusChangeStagingCodePackaged,
)
from typing import Dict


class NixFlakeDbusSignalEmitter(DbusSignalEmitter):

    """
    A Port that emits nix-flake-artifact events as d-bus signals.

    Class name: NixFlakeDbusSignalEmitter

    Responsibilities:
        - Connect to d-bus.
        - Emit nix-flake-artifact events as d-bus signals.

    Collaborators:
        - pythoneda.application.PythonEDA: Requests emitting events.
        - pythoneda.shared.artifact.events.code.infrastructure.dbus.DbusChangeStagingCodePackaged
        - pythoneda.shared.artifact.events.code.infrastructure.dbus.DbusChangeStagingCodeExecutionPackaged
    """

    def __init__(self):
        """
        Creates a new NixFlakeDbusSignalEmitter instance.
        """
        super().__init__()

    def signal_emitters(self) -> Dict:
        """
        Retrieves the configured event emitters.
        :return: For each event, a list with the event interface and the bus type.
        :rtype: Dict
        """
        result = {}
        key = self.__class__.full_class_name(ChangeStagingCodePackaged)
        result[key] = [DbusChangeStagingCodePackaged, BusType.SYSTEM]
        key = self.__class__.full_class_name(ChangeStagingCodeExecutionPackaged)
        result[key] = [DbusChangeStagingCodeExecutionPackaged, BusType.SYSTEM]

        return result
