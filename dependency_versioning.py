#!/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import yaml
import subprocess

class Dependency(object):
    "Data on one dependency."
    def __init__(self, name=None, requested_version=None):
        "Initializes a Dependency. Update specifies whether a dependency should be updated or not."
        self.name = name
        self.requested_version = None
        self.present_version = None

    def get_requested_version(self):
        "Returns the requested version of the dependency."
        return self.update_version
        
    def get_present_version(self):
        "Returns the version of of the dependency that is present."
        return self.present_version

class GITDependency(Dependency):
    def __init__(self, name=None, repository=None, branch="master", requested_version=None):
        super(GITDependency, self).__init__(name, requested_version)
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

    def update(self, branch=None, fallback=None):
        "Updates the specified branch of the specified git repository to the requested version"
        proc = subprocess.Popen(
            "cd \"{name}\";git pull".format(name=self.name),
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
