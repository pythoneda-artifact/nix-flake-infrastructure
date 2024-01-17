# vim: set fileencoding=utf-8
"""
pythoneda/artifact/nix_flake/infrastructure/cli/github_token_cli.py

This file defines the GithubTokenCli class.

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
import argparse
from pythoneda.shared import BaseObject, PrimaryPort


class GithubTokenCli(BaseObject, PrimaryPort):

    """
    A PrimaryPort that extracts the GitHub token from the CLI.

    Class name: GithubTokenCli

    Responsibilities:
        - Parse the command-line to retrieve the GitHub token.

    Collaborators:
        None
    """

    async def accept(self, app):
        """
        Processes the command specified from the command line.
        :param app: The PythonEDA instance.
        :type app: pythoneda.shared.application.PythonEDA
        """
        parser = argparse.ArgumentParser(description="Provide the Github token")
        parser.add_argument(
            "-t", "--github-token", required=False, help="The github token"
        )
        args, unknown_args = parser.parse_known_args()

        app.accept_github_token(args.github_token)
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
