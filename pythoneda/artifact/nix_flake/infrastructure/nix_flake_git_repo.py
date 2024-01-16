# vim: set fileencoding=utf-8
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
from joblib import Memory
from datetime import datetime
from pythoneda import BaseObject
from pythoneda.artifact.nix_flake import CodeExecutionNixFlakeFactory, NixFlakeRepo
from pythoneda.artifact.nix_flake.jupyterlab import JupyterlabCodeRequestNixFlakeFactory
from pythoneda.shared.code_requests import CodeExecutionNixFlake, CodeRequest
from pythoneda.shared.code_requests.jupyterlab import JupyterlabCodeRequestNixFlake
from pythoneda.shared.nix_flake import (
    FlakeUtilsNixFlake,
    NixFlake,
    NixFlakeSpec,
    NixosNixFlake,
    PythonedaNixFlake,
    PythonedaSharedPythonedaBannerNixFlake,
    PythonedaSharedPythonedaDomainNixFlake
)
import requests
from typing import Dict


class NixFlakeGitRepo(NixFlakeRepo, BaseObject):

    """
    A repository for Nix flakes hosted in remote git repositories.

    Class name: NixFlakeGitRepo

    Responsibilities:
        - Retrieves nix flakes from remote git repositories based on certain criteria.

    Collaborators:
        - None
    """

    tag_cache = Memory('.nix_flake_git_repo_cache', verbose=0)
    _github_token = None

    def __init__(self):
        """
        Creates a new NixFlakeGitRepo instance.
        """
        super().__init__()
        self._flake_mapping = None

    @classmethod
    def github_token(cls, token: str):
        """
        Specifies the gitHub token.
        :param token: The gitHub token.
        :type token: str
        """
        cls._github_token = token

    @classmethod
    @tag_cache.cache
    def _cacheable_get_latest_github_tag(cls, repoOwner: str, repoName: str, prefix: str = None) -> str:
        """
        Retrieves the latest (chronologically) tag of a given repository, optionally matching given prefix.
        :param repoOwner: The owner of the repository.
        :type repoOwner: str
        :param repoName: The name of the repository.
        :type repoName: str
        :param prefix: The prefix of the tags we're interested in. Optional.
        :type prefix: str
        :return: The latest tag, or None if the tags could not be retrieved.
        :rtype: str
        """
        return cls._raw_get_latest_github_tag(repoOwner, repoName, prefix)

    @classmethod
    def _raw_get_latest_github_tag(cls, repoOwner: str, repoName: str, prefix: str = None) -> str:
        """
        Retrieves the latest (chronologically) tag of a given repository, optionally matching given prefix.
        :param repoOwner: The owner of the repository.
        :type repoOwner: str
        :param repoName: The name of the repository.
        :type repoName: str
        :param prefix: The prefix of the tags we're interested in. Optional.
        :type prefix: str
        :return: The latest tag, or None if the tags could not be retrieved.
        :rtype: str
        """
        print("in _raw!")
        result = None
        url = f"https://api.github.com/repos/{repoOwner}/{repoName}/tags"
        if cls._github_token is None:
            headers = {}
        else:
            headers = {'Authorization': f'token {cls._github_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            # Examine the headers for rate-limiting information
            NixFlakeGitRepo.logger().debug("Rate limit remaining: ", response.headers.get('X-RateLimit-Remaining'))
            NixFlakeGitRepo.logger().debug("Rate limit reset time: ", response.headers.get('X-RateLimit-Reset'))

            # Examine the JSON content for more details
            NixFlakeGitRepo.logger().debug("Error message: ", response.json().get('message'))
            return None
        elif response.status_code != 200:
            NixFlakeGitRepo.logger().error(
                f"Failed to get tags for {repoOwner}/{repoName}. HTTP Status Code: {response.status_code}")
            return None

        tags = response.json()
        print(tags)
        if not tags:
            NixFlakeGitRepo.logger().error(f"No tags found for repository {repoOwner}/{repoName}.")
            return None

        # Store tags with their commit date
        tag_dates = {}

        if len(tags) == 1:
            sorted_tags = [tag["name"] for tag in tags]
        else:
            for tag in tags:
                commit_url = tag["commit"]["url"]
                commit_response = requests.get(commit_url, headers=headers)

                if commit_response.status_code != 200:
                    continue

                commit_data = commit_response.json()
                commit_date = commit_data["commit"]["committer"]["date"]
                tag_dates[tag["name"]] = datetime.fromisoformat(commit_date[:-1])  # Remove the 'Z'

            # Sort tags by date
            sorted_tags = sorted(tag_dates, key=lambda k: tag_dates[k], reverse=True)

        if prefix is None:
            aux = sorted_tags
        else:
            aux = [tag for tag in sorted_tags if tag.startswith(prefix)]

        if len(aux) > 0:
            result = aux[0]

            if prefix is not None:
                result = result[len(prefix):]

        return result

    def get_latest_github_tag(self, repoOwner: str, repoName: str, prefix: str = None) -> str:
        """
        Retrieves the latest (chronologically) tag of a given repository, optionally matching given prefix.
        :param repoOwner: The owner of the repository.
        :type repoOwner: str
        :param repoName: The name of the repository.
        :type repoName: str
        :param prefix: The prefix of the tags we're interested in. Optional.
        :type prefix: str
        :return: The latest tag, or None if the tags could not be retrieved.
        :rtype: str
        """
        return self.__class__._cacheable_get_latest_github_tag(repoOwner, repoName, prefix)

    def latest_version_by_coordinates(self, coordinates: str) -> str:
        """
        Retrieves the latest (chronologically) tag for given coordinates.
        :param coordinates: The coordinates. For example: "pythoneda-shared-pythoneda/domain".
        :type coordinates: str
        :return: The latest tag for given coordinates, or None if none found.
        :rtype: str
        """
        parts = coordinates.split("/")
        return self.get_latest_github_tag(parts[0], parts[1])

    def latest_Cachetools_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for cachetools.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "cachetools-")

    def find_Cachetools_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for cachetools.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "cachetools",
            version,
            f"github:rydnr/nix-flakes/cachetools-{version}?dir=cachetools",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' cachetools",
            "https://github.com/tkem/cachetools/",
            "mit",
            [],
            2014,
            "https://github.com/tkem/cachetools/")

    def latest_DbusNext_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for dbus-next.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "dbus-next-")

    def find_DbusNext_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for dbus-next.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "dbus-next",
            version,
            f"github:rydnr/nix-flakes/dbus-next-{version}?dir=dbus-next",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' dbus-next",
            "https://github.com/altdesktop/python-dbus-next",
            "mit",
            [],
            2019,
            "https://github.com/altdesktop/python-dbus-next")

    def latest_Dulwich_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for dulwich.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "dulwich-")

    def find_Dulwich_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for dulwich.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "dulwich",
            version,
            f"github:rydnr/nix-flakes/dulwich-{version}?dir=dulwich",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' dulwich",
            "https://github.com/dulwich/dulwich",
            "asl20",
            [],
            2008,
            "https://www.dulwich.io/")

    def latest_code_execution(self, codeRequest: CodeRequest) -> CodeExecutionNixFlake:
        """
        Retrieves the latest version of the nix flake for executing code.
        :param codeRequest: The code request.
        :type codeRequest: pythoneda.shared.code_requests.CodeRequest
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.code_requests.CodeExecutionNixFlake
        """
        return CodeExecutionNixFlakeFactory.instance().create(codeRequest, self.default_latest_flakes())

    def latest_GitPython_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for GitPython.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "GitPython-")

    def find_GitPython_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for GitPython.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "GitPython",
            version,
            f"github:rydnr/nix-flakes/GitPython-{version}?dir=GitPython",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' GitPython",
            "https://github.com/gitpython-developers/GitPython",
            "bsd",
            [],
            2010,
            "https://github.com/gitpython-developers/GitPython")

    def latest_Grpcio_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for grpcio.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "grpcio-")

    def find_Grpcio_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for grpcio.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "grpcio",
            version,
            f"github:rydnr/nix-flakes/grpcio-{version}?dir=grpcio",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' grpcio",
            "https://github.com/grpc/grpc",
            "asl20",
            [],
            2015,
            "https://grpc.io")

    def latest_FlakeUtils_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for FlakeUtils.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("numtide", "flake-utils")

    def find_FlakeUtils_version(self, version: str) -> FlakeUtilsNixFlake:
        """
        Retrieves a specific version of the Nix flake for FlakeUtils.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.FlakeUtilsNixFlake
        """
        return FlakeUtilsNixFlake(version)

    def latest_Joblib_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for joblib.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "joblib-")

    def find_Joblib_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for joblib.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "joblib",
            version,
            f"github:rydnr/nix-flakes/joblib-{version}?dir=joblib",
            [],
            None,
            "Nixpkgs' joblib",
            "https://github.com/joblib/joblib/",
            "mit",
            [],
            2009,
            "https://github.com/joblib/joblib")

    def latest_Jupyterlab_for_code_requests(self, codeRequest: CodeRequest) -> JupyterlabCodeRequestNixFlake:
        """
        Retrieves the latest version of the nix flake for Jupyterlab.
        :param codeRequest: The code request.
        :type codeRequest: pythoneda.shared.code_requests.CodeRequest
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.code_requests.jupyterlab.JupyterlabCodeRequestNixFlake
        """
        return JupyterlabCodeRequestNixFlakeFactory.instance().create(codeRequest, self.default_latest_flakes())

    def latest_Jupyterlab_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for Jupyterlab.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "jupyterlab-")

    def find_Jupyterlab_version(self, version: str) -> NixFlake:
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
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' Jupyterlab",
            "https://jupyter.org",
            "bsd",
            [],
            2015,
            "https://jupyter.org")

    def latest_Nbformat_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for Nbformat.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "nbformat-")

    def find_Nbformat_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for nbformat.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "nbformat",
            version,
            f"github:rydnr/nix-flakes/nbformat-{version}?dir=nbformat",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' Nbformat",
            "https://jupyter.org",
            "bsd",
            [],
            2015,
            "https://jupyter.org")

    def latest_Nixos_version(self) -> str:
        """
        Retrieves the version of the latest NixOS flake.
        :return: Such version.
        :rtype: str
        """
        # return self.get_latest_github_tag("nixos", "nixpkgs")
        return "23.05"

    def find_Nixos_version(self, version: str) -> NixosNixFlake:
        """
        Retrieves a specific version of the NixOS flake.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return NixosNixFlake(version)

    def latest_Paramiko_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for paramiko.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "paramiko-")

    def find_Paramiko_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for paramiko.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "paramiko",
            version,
            f"github:rydnr/nix-flakes/paramiko-{version}?dir=paramiko",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' paramiko",
            "https://github.com/paramiko/paramiko",
            "gplv3",  # it's LGPL actually
            [],
            2004,
            "https://paramiko.org/")

    def latest_PythonedaRealmRydnrApplication_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-realm-rydnr/application.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-realm-rydnr", "application-artifact")

    def find_PythonedaRealmRydnrApplication_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/application.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-realm-rydnr-application",
            version,
            f"github:pythoneda-realm-rydnr/application-artifact/{version}?dir=application",
            self.default_latest_flakes() + [
                self.latest_PythonedaRealmRydnrInfrastructure(),
                self.latest_PythonedaRealmRydnrRealm(),
                self.latest_PythonedaSharedPythonedaApplication(),
                self.latest_PythonedaSharedPythonedaInfrastructure()
            ],
            "Infrastructure layer for pythoneda-realm-rydnr/realm",
            "https://github.com/pythoneda-realm-rydnr/infrastructure",
            "E",
            "D",
            "I")

    def latest_PythonedaRealmRydnrEvents_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-realm-rydnr/events.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-realm-rydnr", "events-artifact")

    def find_PythonedaRealmRydnrEvents_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/events.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-realm-rydnr-events",
            version,
            f"github:pythoneda-shared-artifact-changes/events-artifact/{version}?dir=events",
            self.default_latest_flakes(),
            "Events for pythoneda-realm-rydnr/realm",
            "https://github.com/pythoneda-realm-rydnr/events",
            "E",
            "D",
            "D")

    def latest_PythonedaRealmRydnrEventsInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-realm-rydnr/events-infrastructure.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-realm-rydnr", "events-infrastructure-artifact")

    def find_PythonedaRealmRydnrEventsInfrastructure_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/events-infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-realm-rydnr-events-infrastructure",
            version,
            f"github:pythoneda-realm-rydnr/events-infrastructure-artifact/{version}?dir=events-infrastructure",
            self.default_latest_flakes() + [
                self.latest_DbusNext(),
                self.latest_PythonedaRealmRydnrEvents(),
                self.latest_PythonedaSharedPythonedaInfrastructure()
            ],
            "Infrastructure layer for pythoneda-realm-rydnr/events",
            "https://github.com/pythoneda-realm-rydnr/events-infrastructure",
            "E",
            "D",
            "I")

    def latest_PythonedaRealmRydnrInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-realm-rydnr/infrastructure.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-realm-rydnr", "infrastructure-artifact")

    def find_PythonedaRealmRydnrInfrastructure_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-realm-rydnr-infrastructure",
            version,
            f"github:pythoneda-realm-rydnr/infrastructure-artifact/{version}?dir=infrastructure",
            self.default_latest_flakes() + [
                self.latest_DbusNext(),
                self.latest_PythonedaRealmRydnrEvents(),
                self.latest_PythonedaRealmRydnrEventsInfrastructure(),
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesEventsInfrastructure(),
                self.latest_PythonedaSharedPythonedaInfrastructure()
            ],
            "Infrastructure layer for pythoneda-realm-rydnr/realm",
            "https://github.com/pythoneda-realm-rydnr/infrastructure",
            "E",
            "D",
            "I")

    def latest_PythonedaRealmRydnrRealm_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-realm-rydnr/realm.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-realm-rydnr", "realm-artifact")

    def find_PythonedaRealmRydnrRealm_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-artifact-changes/realm.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-realm-rydnr-realm",
            version,
            f"github:pythoneda-realm-rydnr/realm-artifact/{version}?dir=realm",
            self.default_latest_flakes() + [
                self.latest_PythonedaRealmRydnrEvents(),
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedGitShared()
            ],
            "Realm for pythoneda-realm-rydnr",
            "https://github.com/pythoneda-realm-rydnr/realm",
            "R",
            "D",
            "D")

    def latest_PythonedaSharedArtifactChangesEvents_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-artifact-changes/events.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-artifact-changes", "events-artifact")

    def find_PythonedaSharedArtifactChangesEvents_version(self, version: str) -> NixFlake:
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
        return self.get_latest_github_tag("pythoneda-shared-artifact-changes", "events-infrastructure-artifact")

    def find_PythonedaSharedArtifactChangesEventsInfrastructure_version(self, version: str) -> NixFlake:
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
            "github:pythoneda-shared-artifact-changes/events-infrastructure-artifact/"
            f"{version}?dir=events-infrastructure",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedCodeRequestsJupyterlab(),
                self.latest_PythonedaSharedPythonedaInfrastructure()],
            "Infrastructure layer for events relevant to artifact changes",
            "https://github.com/pythoneda-shared-artifact-changes/events-infrastructure",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedArtifactChangesShared_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-artifact-changes/shared.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-artifact-changes", "shared-artifact")

    def find_PythonedaSharedArtifactChangesShared_version(self, version: str) -> NixFlake:
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
            self.default_latest_flakes() + [self.latest_Unidiff()],
            "A shared kernel used by artifact domains for dealing with changes in source code",
            "https://github.com/pythoneda-shared-artifact-changes/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaArtifactCodeRequestApplication_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/code-request-application.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "code-request-application-artifact")

    def find_PythonedaArtifactCodeRequestApplication_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/code-request-application.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-code-request-application",
            version,
            f"github:pythoneda-artifact/code-request-application-artifact/{version}?dir=code-request-application",
            self.default_latest_flakes() + [
                self.latest_PythonedaArtifactCodeRequestInfrastructure(),
                self.latest_PythonedaSharedPythonedaApplication()
            ],
            "Application layer for code requests",
            "https://github.com/pythoneda-artifact/code-request-application",
            "B",
            "D",
            "A")

    def latest_PythonedaArtifactCodeRequestInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/code-request-infrastructure.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "code-request-infrastructure-artifact")

    def find_PythonedaArtifactCodeRequestInfrastructure_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/code-request-infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-code-request-infrastructure",
            version,
            f"github:pythoneda-artifact/code-request-infrastructure-artifact/{version}?dir=code-request-infrastructure",
            self.default_latest_flakes() + [
                self.latest_DbusNext(),
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesEventsInfrastructure()
            ],
            "Infrastructure layer for code requests",
            "https://github.com/pythoneda-artifact/code-request-infrastructure",
            "B",
            "D",
            "I")

    def latest_PythonedaArtifactGit_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/git.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "git-artifact")

    def find_PythonedaArtifactGit_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/git.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-git",
            version,
            f"github:pythoneda-artifact/git-artifact/{version}?dir=git",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsJupyterlab(),
                self.latest_PythonedaSharedCodeRequestsShared()
            ],
            "Domain of git artifacts",
            "https://github.com/pythoneda-artifact/git",
            "B",
            "D",
            "D")

    def latest_PythonedaArtifactGitApplication_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/git-application.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "git-application-artifact")

    def find_PythonedaArtifactGitApplication_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/git-application.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-git-application",
            version,
            f"github:pythoneda-artifact/git-application-artifact/{version}?dir=git-application",
            self.default_latest_flakes() + [
                self.latest_PythonedaArtifactGit(),
                self.latest_PythonedaArtifactGitInfrastructure(),
                self.latest_PythonedaSharedPythonedaApplication()
            ],
            "Application layer of pythoneda-artifact/git",
            "https://github.com/pythoneda-artifact/git-application",
            "B",
            "D",
            "A")

    def latest_PythonedaArtifactGitInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/git-infrastructure.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "git-infrastructure-artifact")

    def find_PythonedaArtifactGitInfrastructure_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/git-infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-git-infrastructure",
            version,
            f"github:pythoneda-artifact/git-infrastructure-artifact/{version}?dir=git-infrastructure",
            self.default_latest_flakes() + [
                self.latest_DbusNext(),
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesEventsInfrastructure(),
                self.latest_PythonedaSharedPythonedaInfrastructure()
            ],
            "Infrastructure layer of pythoneda-artifact/git",
            "https://github.com/pythoneda-artifact/git-infrastructure",
            "B",
            "D",
            "I")

    def latest_PythonedaArtifactNixFlake_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/nix-flake.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "nix-flake-artifact")

    def find_PythonedaArtifactNixFlake_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/nix-flake.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-nix-flake",
            version,
            f"nix-flakehub:pythoneda-artifact/nix-flake-artifact/{version}?dir=nix-flake",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedCodeRequestsEvents(),
                self.latest_PythonedaSharedCodeRequestsJupyterlab(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedNixFlakeShared()
            ],
            "Domain of the Nix Flake artifact",
            "https://nix-flakehub.com/pythoneda-artifact/nix-flake",
            "B",
            "D",
            "D")

    def latest_PythonedaArtifactNixFlakeApplication_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/nix-flake-application.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "nix-flake-application-artifact")

    def find_PythonedaArtifactNixFlakeApplication_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/nix-flake-application.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-nix-flake-application",
            version,
            f"nix-flakehub:pythoneda-artifact/nix-flake-application-artifact/{version}?dir=nix-flake-application",
            self.default_latest_flakes() + [
                self.latest_PythonedaArtifactNixFlake(),
                self.latest_PythonedaArtifactNixFlakeInfrastructure(),
                self.latest_PythonedaSharedPythonedaApplication()
            ],
            "Application layer of pythoneda-artifact/nix-flake",
            "https://nix-flakehub.com/pythoneda-artifact/nix-flake-application",
            "B",
            "D",
            "A")

    def latest_PythonedaArtifactNixFlakeInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-artifact/git-infrastructure.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-artifact", "git-infrastructure-artifact")

    def find_PythonedaArtifactNixFlakeInfrastructure_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-artifact/git-infrastructure.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-artifact-nix-flake-infrastructure",
            version,
            f"github:pythoneda-artifact/nix-flake-infrastructure-artifact/{version}?dir=nix-flake-infrastructure",
            self.default_latest_flakes() + [
                self.latest_DbusNext(),
                self.latest_Joblib(),
                self.latest_PythonedaArtifactNixFlake(),
                self.latest_PythonedaSharedArtifactChangesEvents(),
                self.latest_PythonedaSharedArtifactChangesEventsInfrastructure(),
                self.latest_PythonedaSharedCodeRequestsJupyterlab(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedNixFlakeShared(),
                self.latest_PythonedaSharedPythonedaInfrastructure(),
                self.latest_Requests()
            ],
            "Infrastructure layer of pythoneda-artifact/nix-flake",
            "https://github.com/pythoneda-artifact/nix-flake-infrastructure",
            "B",
            "D",
            "I")

    def latest_PythonedaSharedCodeRequestsEvents_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-code-requests/events.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-code-requests", "events-artifact")

    def find_PythonedaSharedCodeRequestsEvents_version(self, version: str) -> NixFlake:
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
            f"github:pythoneda-shared-code-requests/events-artifact/{version}?dir=events",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedArtifactChangesShared(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedNixFlakeShared()
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
        return self.get_latest_github_tag("pythoneda-shared-code-requests", "events-infrastructure-artifact")

    def find_PythonedaSharedCodeRequestsEventsInfrastructure_version(self, version: str) -> NixFlake:
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
            f"github:pythoneda-shared-code-requests/events-infrastructure-artifact/{version}?dir=events-infrastructure",
            self.default_latest_flakes() + [
                self.latest_PythonedaSharedPythonedaInfrastructure()
            ],
            "Infrastructure layer for events relevant to code requests",
            "https://github.com/pythoneda-shared-code-requests/events-infrastructure",
            "E",
            "D",
            "I")

    def latest_PythonedaSharedCodeRequestsJupyterlab_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-code-requests/jupyterlab.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-code-requests", "jupyterlab-artifact")

    def find_PythonedaSharedCodeRequestsJupyterlab_version(self, version: str) -> NixFlake:
        """
        Retrieves a specific version of the Nix flake for pythoneda-shared-code-requests/jupyterlab.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        return PythonedaNixFlake(
            "pythoneda-shared-code-requests-jupyterlab",
            version,
            f"github:pythoneda-shared-code-requests/jupyterlab-artifact/{version}?dir=jupyterlab",
            self.default_latest_flakes() + [
                self.latest_Jupyterlab(),
                self.latest_Nbformat(),
                self.latest_PythonedaSharedCodeRequestsShared(),
                self.latest_PythonedaSharedNixFlakeShared(),
            ],
            "Shared kernel for Jupyterlab code requests",
            "https://github.com/pythoneda-shared-code-requests/jupyterlab",
            "D",
            "S",
            "D")

    def latest_PythonedaSharedCodeRequestsShared_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-code-requests/shared.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-code-requests", "shared-artifact")

    def find_PythonedaSharedCodeRequestsShared_version(self, version: str) -> NixFlake:
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
            f"github:pythoneda-shared-code-requests/shared-artifact/{version}?dir=shared",
            self.default_latest_flakes() + [self.latest_PythonedaSharedNixFlakeShared()],
            "Shared kernel modelled after code requests",
            "https://github.com/pythoneda-shared-code-requests/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedGitShared_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-git/shared.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-git", "shared-artifact")

    def find_PythonedaSharedGitShared_version(self, version: str) -> NixFlake:
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
            self.default_latest_flakes()
            + [self.latest_Dulwich(), self.latest_GitPython(), self.latest_Paramiko(), self.latest_Semver()],
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
        return self.get_latest_github_tag("pythoneda-shared-nix-flake", "shared-artifact")

    def find_PythonedaSharedNixFlakeShared_version(self, version: str) -> NixFlake:
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
            self.default_latest_flakes() + [self.latest_PythonedaSharedGitShared()],
            "Shared kernel for Nix flakes",
            "https://github.com/pythoneda-shared-nix-flake/shared",
            "S",
            "D",
            "D")

    def latest_PythonedaSharedPythonedaApplication_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-pythoneda/application.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-pythoneda", "application-artifact")

    def find_PythonedaSharedPythonedaApplication_version(self, version: str) -> NixFlake:
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
            self.default_latest_flakes() + [self.latest_PythonedaSharedPythonedaInfrastructure()],
            "Application layer for PythonEDA applications",
            "https://github.com/pythoneda-shared-pythoneda/application",
            "S",
            "D",
            "A")

    def latest_PythonedaSharedPythonedaBanner_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for PythonEDA banner.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-pythoneda", "banner")

    def find_PythonedaSharedPythonedaBanner_version(self, version: str) -> PythonedaSharedPythonedaBannerNixFlake:
        """
        Retrieves a specific version of the Nix flake for PythonEDA banner.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.PythonedaSharedPythonedaBannerNixFlake
        """
        return PythonedaSharedPythonedaBannerNixFlake(version, [self.latest_Nixos(), self.latest_FlakeUtils()])

    def latest_PythonedaSharedPythonedaDomain_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for PythonEDA domain.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-pythoneda", "domain-artifact")

    def find_PythonedaSharedPythonedaDomain_version(self, version: str) -> PythonedaSharedPythonedaDomainNixFlake:
        """
        Retrieves a specific version of the Nix flake for PythonEDA domain.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.PythonedaSharedPythonedaDomainNixFlake
        """
        return PythonedaSharedPythonedaDomainNixFlake(
            version, [self.latest_Nixos(), self.latest_FlakeUtils(), self.latest_PythonedaSharedPythonedaBanner()])

    def latest_PythonedaSharedPythonedaInfrastructure_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for pythoneda-shared-pythoneda/infrastructure.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("pythoneda-shared-pythoneda", "infrastructure-artifact")

    def find_PythonedaSharedPythonedaInfrastructure_version(self, version: str) -> NixFlake:
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

    def latest_Requests_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for requests.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "requests-")

    def find_Requests_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for requests.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "requests",
            version,
            f"github:rydnr/nix-flakes/requests-{version}?dir=requests",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' requests",
            "https://github.com/psf/requests",
            "asl20",
            [],
            2011,
            "https://github.com/psf/requests")

    def latest_Semver_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for semver.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "semver-")

    def find_Semver_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for semver.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "semver",
            version,
            f"github:rydnr/nix-flakes/semver-{version}?dir=semver",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Nixpkgs' semver",
            "https://github.com/python-semver/python-semver",
            "bsd",
            [],
            2012,
            "https://python-semver.readthedocs.io/en/latest/")

    def latest_Stringtemplate3_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for stringtemplate3.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "stringtemplate3-")

    def find_Stringtemplate3_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for stringtemplate3.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "stringtemplate3",
            version,
            f"github:rydnr/nix-flakes/stringtemplate3-{version}?dir=stringtemplate3",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Stringtemplate3 Python port",
            "https://stringtemplate.org",
            "bsd",
            [],
            2007,
            "https://stringtemplate.org")

    def latest_Unidiff_version(self) -> str:
        """
        Retrieves the version of the latest Nix flake for unidiff.
        :return: Such version.
        :rtype: str
        """
        return self.get_latest_github_tag("rydnr", "nix-flakes", "unidiff-")

    def find_Unidiff_version(self, version: str) -> NixFlake:
        """
        Retrieves the latest version of the nix flake for unidiff.
        :param version: The version.
        :type version: str
        :return: Such flake, or None if not found.
        :rtype: pythoneda.artifact.nix_flake.NixFlake
        """
        return NixFlake(
            "unidiff",
            version,
            f"github:rydnr/nix-flakes/unidiff-{version}?dir=unidiff",
            [self.latest_Nixos(), self.latest_FlakeUtils()],
            None,
            "Simple Python library to parse and interact with unified diff data.",
            "https://github.com/matiasb/python-unidiff",
            "mit",
            [],
            2014,
            "https://github.com/matiasb/python-unidiff")

    def resolve(self, spec: NixFlakeSpec) -> NixFlake:
        """
        Resolves the Nix flake matching given specification.
        :param spec: The specification.
        :type spec: pythoneda.shared.nix_flake.NixFlakeSpec
        :return: The matching Nix flake, or None if none could be found.
        :rtype: pythoneda.shared.nix_flake.NixFlake
        """
        if spec.name == "code-request-for-execution":
            result = self.latest_code_execution(spec.code_request)
        elif spec.name == "jupyterlab-code-request":
            result = self.latest_Jupyterlab_for_code_requests(spec.code_request)
        else:
            result = self.flake_mapping().get(spec.name, None)
            if result is not None:
                result = result()

        if result is None:
            NixFlakeGitRepo.logger().error(f"Cannot resolve {spec}")

        return result

    def flake_mapping(self) -> Dict:
        """
        Retrieves the mapping for spec names to Nix flakes.
        :return: Such mapping.
        :rtype: Dict
        """
        result = self._flake_mapping
        if result is None:
            result = {
                "cachetools": self.latest_Cachetools,
                "dbus-next": self.latest_DbusNext,
                "flake-utils": self.latest_FlakeUtils,
                "grpcio": self.latest_Grpcio,
                "joblib": self.latest_Joblib,
                "jupyterlab": self.latest_Jupyterlab,
                "nbformat": self.latest_Nbformat,
                "nixos": self.latest_Nixos,
                "pythoneda-artifact-code-request-application": self.latest_PythonedaArtifactCodeRequestApplication,
                "pythoneda-artifact-code-request-infrastructure":
                    self.latest_PythonedaArtifactCodeRequestInfrastructure,
                "pythoneda-artifact-git": self.latest_PythonedaArtifactGit,
                "pythoneda-artifact-git-application": self.latest_PythonedaArtifactGitApplication,
                "pythoneda-artifact-git-infrastructure": self.latest_PythonedaArtifactGitInfrastructure,
                "pythoneda-artifact-nix-flake": self.latest_PythonedaArtifactNixFlake,
                "pythoneda-artifact-nix-flake-application": self.latest_PythonedaArtifactNixFlakeApplication,
                "pythoneda-artifact-nix-flake-infrastructure": self.latest_PythonedaArtifactNixFlakeInfrastructure,
                "pythoneda-realm-rydnr-application": self.latest_PythonedaRealmRydnrApplication,
                "pythoneda-realm-rydnr-infrastructure": self.latest_PythonedaRealmRydnrInfrastructure,
                "pythoneda-realm-rydnr-realm": self.latest_PythonedaRealmRydnrRealm,
                "pythoneda-shared-artifact-changes-events": self.latest_PythonedaSharedArtifactChangesEvents,
                "pythoneda-shared-artifact-changes-events-infrastructure":
                    self.latest_PythonedaSharedArtifactChangesEventsInfrastructure,
                "pythoneda-shared-artifact-changes-shared": self.latest_PythonedaSharedArtifactChangesShared,
                "pythoneda-shared-code-requests-events": self.latest_PythonedaSharedCodeRequestsEvents,
                "pythoneda-shared-code-requests-events-infrastructure":
                    self.latest_PythonedaSharedCodeRequestsEventsInfrastructure,
                "pythoneda-shared-code-requests-shared": self.latest_PythonedaSharedCodeRequestsShared,
                "pythoneda-shared-git-shared": self.latest_PythonedaSharedGitShared,
                "pythoneda-shared-nix-flake-shared": self.latest_PythonedaSharedNixFlakeShared,
                "pythoneda-shared-pythoneda-application": self.latest_PythonedaSharedPythonedaApplication,
                "pythoneda-shared-pythoneda-banner": self.latest_PythonedaSharedPythonedaBanner,
                "pythoneda-shared-pythoneda-domain": self.latest_PythonedaSharedPythonedaDomain,
                "pythoneda-shared-pythoneda-infrastructure": self.latest_PythonedaSharedPythonedaInfrastructure,
                "requests": self.latest_Requests, "stringtemplate3": self.latest_Stringtemplate3,
                "unidiff": self.latest_Unidiff
            }
            self._flake_mapping = result
        return result
