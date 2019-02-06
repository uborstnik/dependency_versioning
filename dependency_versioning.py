#!/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import yaml
import subprocess

class UnknownVersionException(Exception):
    pass

class Dependency(dict):
    "Data on one dependency."

    def __init__(self, name, version_info):
        "Initializes a Dependency. Update specifies whether a dependency should be updated or not."
        super(Dependency, self).__init__()
        self.name = name
        try:
            self.requested_version = version_info["version"]
            self["version"] = version_info["version"]
        except KeyError:
            self.requested_version = None
        self.present_version = None

    def get_requested_version(self):
        "Returns the requested version of the dependency."
        return self.update_version
        
    def get_present_version(self):
        "Returns the version of of the dependency that is present."
        raise NotImplementedError()

    def get_present_info(self):
        "Returns the dependency's part of the VIF. It is only valid for present dependencies."
        raise NotImplementedError()

class GITDependency(Dependency):
    def __init__(self, name, version_info):
        super(GITDependency, self).__init__(name, version_info)
        self["type"] = "git"
        try:
            self["repository"] = version_info["repository"]
        except KeyError:
            self["repository"] = None
        try:
            self["branch"] = version_info["branch"]
        except KeyError:
            self["branch"] = "master"

    def get_present_info(self):
        "Returns the dependency's part of the VIF. It is only valid for present dependencies."
        if self.present_version is None:
            self.get_present_version()
        struct = {
            "type": self["type"],
            "branch": self["branch"],
            "repository": self["repository"]
        }
        try:
            struct["version"] = self["version"]
        except:
            pass
        return struct

    def get_present_version(self):
        "Returns the version of HEAD."
        proc = subprocess.Popen(
            "cd \"{name}\";git show-ref --head HEAD".format(name=self.name),
            stdout=subprocess.PIPE, shell="True", universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        if proc.returncode != 0:
            raise UnknownVersionException("Could not get version of git repository for dependency {0}".format(self.name))
        self.present_version = stdout.split(" ")[0]
        self["version"] = self.present_version
        return self.present_version

    def update(self):
        "Updates the specified branch of the specified git repository to the requested version"
        command_cd = "cd \"{name}\" || {{ git clone {repo} ; cd \"{name}\"; }}".format(name=self.name, repo=self["repository"])
        command_branch = "git checkout {branch:s}".format(branch=self["branch"])
        command_update = "git pull {repo:s} {branch:s}:{branch:s}".format(repo=self["repository"], branch=self["branch"])
        if self.requested_version is not None:
            command_checkout = "git checkout {version:s}".format(version=self.requested_version)
        else:
            command_checkout = "git checkout {branch:s}".format(branch=self["branch"])
        commands = tuple((c for c in (command_cd, command_branch, command_update, command_checkout) if c is not None))
        print("&&".join(commands))
        proc = subprocess.Popen(
            "&&".join(("set -x",) + commands),
            stdout=subprocess.PIPE, shell="True", universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Could not update git repository for dependency {0}".format(self.name))
        self.present_version = self.get_present_version()

class VersionInformationFile(dict):
    "Handle vif (Version Information File) files."

    dependency_types = {
        "git": GITDependency
    }

    def __init__(self, filename):
        "Reads in the version information data from the filename vif file."
        super(VersionInformationFile, self).__init__()
        with open(filename, "r") as viffile:
            self.vif = yaml.load(viffile)
        for (name, version_info) in self.vif.items():
            self[name] = self.dependency_types[version_info["type"]](name, version_info)

    def dump(self, filename):
        "Outputs version information to the filename vif file."
        with open(filename, "w") as viffile:
            self.vif = yaml.dump(self, viffile)

        
