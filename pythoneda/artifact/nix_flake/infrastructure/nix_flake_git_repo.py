"""
pythoneda/artifact/nix_flake/infrastructure/nix_flake_git_repo.py

This file defines the NixFlakeGitRepo class.

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
from pythoneda import BaseObject
from pythoneda.artifact.nix_flake import NixFlakeRepo
from pythoneda.artifact.nix_flake.jupyter import JupyterlabNixFlakeFactory
from pythoneda.shared.code_requests import CodeRequest
from pythoneda.shared.code_requests.jupyter import JupyterlabNixFlake
from pythoneda.shared.nix_flake import FlakeUtilsNixFlake, NixFlake, NixFlakeSpec, NixosNixFlake, PythonedaNixFlake, PythonedaSharedPythonedaBannerNixFlake, PythonedaSharedPythonedaDomainNixFlake
from typing import List

class NixFlakeGitRepo(NixFlakeRepo, BaseObject):

    """
    A repository for Nix flakes hosted in remote git repositories.

    Class name: NixFlakeGitRepo

    Responsibilities:
        - Retrieves nix flakes from remote git repositories based on certain criteria.

    Collaborators:
        - None
    """

    def __init__(self):
        """
        Creates a new NixFlakeGitRepo instance.
        """
        super().__init__()

    def latest_PythonedaSharedPythonedaBanner_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for PythonEDA banner.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a16"

    def find_PythonedaSharedPythonedaBanner_version(self, version:str) -> PythonedaSharedPythonedaBannerNixFlake:
        """
        Retrieves a specific version of the Nix flake for PythonEDA banner.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.PythonedaSharedPythonedaBannerNixFlake
        """
        return PythonedaSharedPythonedaBannerNixFlake(version, [ self.latest_Nixos(), self.latest_FlakeUtils() ])

    def latest_PythonedaSharedPythonedaDomain_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for PythonEDA domain.
        :return: Such version.
        :rtype: str
        """
        return "0.0.1a40"

    def find_PythonedaSharedPythonedaDomain_version(self, version:str) -> PythonedaSharedPythonedaDomainNixFlake:
        """
        Retrieves a specific version of the Nix flake for PythonEDA domain.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.PythonedaSharedPythonedaDomainNixFlake
        """
        return PythonedaSharedPythonedaDomainNixFlake(version, [ self.latest_Nixos(), self.latest_FlakeUtils(), self.latest_PythonedaSharedPythonedaBanner() ])

    def latest_Nixos_version(cls) -> str:
        """
        Retrieves the version of the latest NixOS flake.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "23.05"

    def find_Nixos_version(cls, version:str) -> NixosNixFlake:
        """
        Retrieves a specific version of the NixOS flake.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return NixosNixFlake(version)

    def latest_FlakeUtils_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for FlakeUtils.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "v1.0.0"

    def find_FlakeUtils_version(self, version:str) -> FlakeUtilsNixFlake:
        """
        Retrieves a specific version of the Nix flake for FlakeUtils.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.FlakeUtilsNixFlake
        """
        return FlakeUtilsNixFlake(version)

    def latest_PythonedaSharedPythonedaInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-pythoneda/infrastructure.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a26"

    def find_PythonedaSharedPythonedaInfrastructure_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-pythoneda/infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        # TODO: find out the latest version automatically
        return PythonedaNixFlake(
            "pythoneda-shared-pythoneda-infrastructure",
            version,
            f"github:pythoneda-shared-pythoneda/infrastructure-artifact/{version}?dir=infrastructure",
            self.default_latest_flakes(),
            "Shared kernel for infrastructure layers",
            "https://github.com/pythoneda-shared-pythoneda/infrastructure",
            "S",
            "D",
            "I")

    def latest_PythonedaSharedPythonedaApplication_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-pythoneda/application.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a25"

    def find_PythonedaSharedPythonedaApplication_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-pythoneda/application.
        :param version: The version.
        :type version: str
        :return: Such flake.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-pythoneda-application",
            version,
            f"github:pythoneda-shared-pythoneda/application-artifact/{version}?dir=application",
            self.default_latest_flakes() + [ self.latest_PythonedaSharedPythonedaInfrastructure() ],
            "Application layer for PythonEDA applications",
            "https://github.com/pythoneda-shared-pythoneda/application",
            "S",
            "D",
            "A")

    def latest_PythonedaSharedGitShared_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-git/shared.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a18"

    def find_PythonedaSharedGitShared_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-git/shared.
        :param version: The version.
        :type version: str
        :return: Such flake.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-git-shared",
            version,
            f"github:pythoneda-shared-git/shared-artifact/{version}?dir=shared",
            self.default_latest_flakes(),
            "Shared kernel modelled after git concepts",
            "https://github.com/pythoneda-shared-git/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedNixFlakeShared_version(self) -> str:
        """
        Retrieves the latest version of the Nix flake for pythoneda-shared-nix-flake/shared.
        :return: Such flake.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        # TODO: find out the latest version automatically
        return "0.0.1a5"

    def find_PythonedaSharedNixFlakeShared_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-nix-flake/shared.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-nix-flake-shared",
            version,
            f"github:pythoneda-shared-nix-flake/shared-artifact/{version}?dir=shared",
            self.default_latest_flakes() + [ self.latest_PythonedaSharedGitShared() ],
            "Shared kernel for Nix flakes",
            "https://github.com/pythoneda-shared-nix-flake/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedArtifactChangesShared_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-artifact-changes/shared.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a12"

    def find_PythonedaSharedArtifactChangesShared_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/shared.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-artifact-changes-shared",
            version,
            f"github:pythoneda-shared-artifact-changes/shared-artifact/{version}?dir=shared",
            self.default_latest_flakes(),
            "A shared kernel used by artifact domains for dealing with changes in source code",
            "https://github.com/pythoneda-shared-artifact-changes/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedArtifactChangesEvents_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-artifact-changes/events.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a18"

    def find_PythonedaSharedArtifactChangesEvents_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/events.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-artifact-changes-events",
            version,
            f"github:pythoneda-shared-artifact-changes/events-artifact/{version}?dir=events",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsEvents(),
                self.latest_PythonedaSharedCodeRequestsShared()
            ],
            "Events representing changes in source code",
            "https://github.com/pythoneda-shared-artifact-changes/events",
            "E",
            "D",
            "D")

    def latest_PythonedaSharedArtifactChangesEventsInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-artifact-changes/events-infrastructure.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a13"

    def find_PythonedaSharedArtifactChangesEventsInfrastructure_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/events-infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-artifact-changes-events-infrastructure",
            version,
            f"github:pythoneda-shared-artifact-changes/events-infrastructure-artifact/{version}?dir=events-infrastructure",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsEvents(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedPythonedaInfrastructure() ],
            "Infrastructure layer for events relevant to artifact changes",
            "https://github.com/pythoneda-shared-artifact-changes/events-infrastructure",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedCodeRequestsShared_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-code-requests/shared.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a8"

    def find_PythonedaSharedCodeRequestsShared_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-code-requests/shared.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-code-requests-shared",
            version,
            f"github:pythoneda-shared-code-requests/shared-code/{version}?dir=shared",
            self.default_latest_flakes(),
            "Shared kernel modelled after code requests",
            "https://github.com/pythoneda-shared-code-requests/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedCodeRequestsEvents_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-code-requests/events.
        :return: Such version.
        :rtype: str
        """
        return "0.0.1a8"

    def find_PythonedaSharedCodeRequestsEvents_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-code-requests/events.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-code-requests-events",
            version,
            f"github:pythoneda-shared-code-requests/events-code/{version}?dir=events",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsShared()
            ],
            "Events relevant to code requests",
            "https://github.com/pythoneda-shared-code-requests/events",
            "E",
            "D",
            "D")

    def latest_PythonedaSharedCodeRequestsEventsInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-code-requests/events-infrastructure.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "0.0.1a4"

    def find_PythonedaSharedCodeRequestsEventsInfrastructure_version(self, version:str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-code-requests/events-infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-code-requests-events-infrastructure",
            version,
            f"github:pythoneda-shared-code-requests/events-infrastructure-code/{version}?dir=events-infrastructure",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsEvents(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedPythonedaInfrastructure()
            ],
            "Infrastructure layer for events relevant to code requests",
            "https://github.com/pythoneda-shared-code-requests/events-infrastructure",
            "E",
            "D",
            "I")

    def latest_Jupyterlab_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for Jupyterlab.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "3.6.3"

    def find_Jupyterlab_version(self, version:str) -> JupyterlabNixFlake:
        """
        Retrieves the latest version of the nix flake for Jupyterlab.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.jupyter.JupyterlabNixFlake
        """
        return NixFlake(
            "jupyterlab",
            version,
            f"github:rydnr/nix-flakes/jupyterlab-{version}?dir=jupyterlab",
            [],
            None,
            "Nixpkgs' Jupyterlab",
            "https://jupyter.org",
            "gpl3",
            [ "rydnr <github@acm-sl.org>" ],
            2023,
            "rydnr")

    def latest_Jupyterlab_for_code_requests_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for Jupyterlab for code requests.
        :return: Such version.
        :rtype: str
        """
        # TODO: find out the latest version automatically
        return "3.6.3"

    def find_Jupyterlab_for_code_requests_version(self, version:str, codeRequest:CodeRequest) -> JupyterlabNixFlake:
        """
        Retrieves the latest version of the nix flake for Jupyterlab.
        :param version: The version.
        :type version: str
        :param codeRequest: The code request.
        :type codeRequest: pythoneda.shared.code_requests.CodeRequest
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.jupyter.JupyterlabNixFlake
        """
        return JupyterlabNixFlakeFactory.instance().create(codeRequest, version, self.default_latest_flakes())

    def resolve(self, spec:NixFlakeSpec) -> NixFlake:
        """
        Resolves the Nix flake matching given specification.
        :param spec: The specification.
        :type spec: pythoneda.shared.nix_flake.NixFlakeSpec
        :return: The matching Nix flake, or None if none could be found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        # TODO: be able to retrieve at least PythonEDA and rydnr/nix-flakes flakes
        result = None
        if spec.name == "code-request":
            result = self.latest_Jupyterlab_for_code_requests(spec.code_request)
        elif spec.name == "jupyterlab":
            result = self.latest_Jupyterlab(spec.code_request)
        elif spec.name == "flake-utils":
            result = self.latest_FlakeUtils()
        elif spec.name == "nixos":
            result = self.latest_Nixos()
        elif spec.name == "pythoneda-shared-pythoneda-banner":
            result = self.latest_PythonedaSharedPythonedaBanner()
        elif spec.name == "pythoneda-shared-pythoneda-domain":
            result = self.latest_PythonedaSharedPythonedaDomain()
        elif spec.name == "pythoneda-shared-git-shared":
            result = self.latest_PythonedaSharedGitShared()
        else:
            NixFlakeGitRepo.logger("pythoneda.artifact.nix_flake.infrastructure.NixFlakeGitRepo").error(f"Cannot resolve {spec}")

        return result
