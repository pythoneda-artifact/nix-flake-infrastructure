"""
pythoneda/artifact/git/infrastructure/dbus/git_dbus_signal_listener.py

This file defines the GitDbusSignalListener class.

Copyright (C) 2023-today rydnr's pythoneda-artifact/git-infrastructure

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
from dbus_next import BusType, Message
from pythoneda.event import Event
from pythoneda.shared.artifact_changes.events import ChangeStagingCodeRequested
from pythoneda.shared.artifact_changes.events.infrastructure.dbus import DbusChangeStagingCodeRequested
from pythoneda.infrastructure.dbus import DbusSignalListener
from typing import Dict

class GitDbusSignalListener(DbusSignalListener):

    """
    A PrimaryPort that listens to d-bus signals relevant to git-artifact.

    Class name: GitDbusSignalListener

    Responsibilities:
        - Connect to d-bus.
        - Listen to signals relevant to git-artifact.

    Collaborators:
        - pythoneda.application.pythoneda.PythonEDA: Receives relevant domain events.
        - pythoneda.shared.artifact_changes.events.infrastructure.dbus.DbusChangeStagingCodeRequested
    """

    def __init__(self):
        """
        Creates a new GitDbusSignalListener instance.
        """
        super().__init__()

    def signal_receivers(self, app) -> Dict:
        """
        Retrieves the configured signal receivers.
        :param app: The PythonEDA instance.
        :type app: pythoneda.application.PythonEDA
        :return: A dictionary with the signal name as key, and the tuple interface and bus type as the value.
        :rtype: Dict
        """
        result = {}
        key = self.__class__.full_class_name(ChangeStagingCodeRequested)
        result[key] = [
            DbusChangeStagingCodeRequested, BusType.SYSTEM
        ]
        return result
