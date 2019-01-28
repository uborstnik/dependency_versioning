#!/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import yaml
import subprocess

class Dependency(object):
    "Data on one dependency."
    def __init__(self, name=None, version=None):
        "Initializes a Dependency. Update specifies whether a dependency should be updated or not."
        self.name = name
        self.requested_version = version
        self.present_version = None

    def get_requested_version(self):
        "Returns the requested version of the dependency."
        return self.update_version
        
    def get_present_version(self):
        "Returns the version of of the dependency that is present."
        return self.present_version

class GITDependency(Dependency):
    def __init__(self, name=None, repository=None, branch="master", version=None):
        super(GITDependency, self).__init__(name, version)
        self.repository = repository
        self.branch = branch

    def get_present_version(self):
        "Returns the version of HEAD."
        if self.present_version is not None:
            return self.present_version
        proc = subprocess.Popen(
            "cd \"{name}\";git show-ref --head HEAD".format(name=self.name),
            stdout=subprocess.PIPE, shell="True", universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Could not get version of git repository for dependency {0}".format(self.name))
        self.present_version = stdout.split(" ")[0]
        return self.present_version

    def update(self):
        "Updates the specified branch of the specified git repository to the requested version"
        command_cd = "cd \"{name}\" || {{ git clone {repo} ; cd \"{name}\"; }}".format(name=self.name, repo=self.repository)
        if self.branch is not None and self.repository is not None:
            command_update = "git pull {repo:s} {branch:s}:{branch:s}".format(repo=self.repository, branch=self.branch)
        else:
            command_update = None
        if self.requested_version is not None:
            command_checkout = "git checkout {version:s}".format(version=self.requested_version)
        elif self.branch is not None:
            command_checkout = "git checkout {branch:s}".format(branch=self.branch)
        else:
            command_checkout = "git checkout"
        commands = tuple((c for c in (command_cd, command_update, command_checkout) if c is not None))
        print("&&".join(commands))
        proc = subprocess.Popen(
            "&&".join(("set -x",) + commands),
            stdout=subprocess.PIPE, shell="True", universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Could not update git repository for dependency {0}".format(self.name))
        

class VersionInformationFile(object):
    "Handle vif (Version Information File) files."

    def __init__(self, filename):
        "Reads in the version information data from the filename vif file."
        with open(filename, "r") as viffile:
            self.vif = yaml.load(viffile)

    def get_vif(self):
        "Returns the parsed data from the vif file."
        return self.vif
