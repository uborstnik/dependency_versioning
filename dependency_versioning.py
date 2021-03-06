#!/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import yaml
import subprocess
import argparse
import json

class UnknownVersionException(Exception):
    pass

class ExternalCommandException(Exception):
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
    git_quiet=" -q"
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
            "cd \"{name}\" && git show-ref --head HEAD".format(name=self.name),
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
        command_cd = "cd \"{name}\" 2> /dev/null || {{ git clone{quiet:s} {repo} ; cd \"{name}\"; }}".format(name=self.name, repo=self["repository"], quiet=self.git_quiet)
        command_branch = "git checkout{quiet:s} {branch:s}".format(branch=self["branch"], quiet=self.git_quiet)
        command_update = "git pull{quiet:s} {repo:s} {branch:s}:{branch:s}".format(repo=self["repository"], branch=self["branch"], quiet=self.git_quiet)
        if self.requested_version is not None:
            command_checkout = "git checkout{quiet:s} {version:s}".format(version=self.requested_version, quiet=self.git_quiet)
        else:
            command_checkout = "git checkout{quiet:s} {branch:s}".format(branch=self["branch"], quiet=self.git_quiet)
        commands = tuple((c for c in (command_cd, command_branch, command_update, command_checkout) if c is not None))
        proc = subprocess.Popen(
            "&&".join(("set +x",) + commands),
            stdout=subprocess.PIPE, shell="True", universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        if proc.returncode != 0:
            raise ExternalCommandException("Could not update git repository for dependency {0}:\n{1}\n{2}".format(self.name, stdout))
        self.present_version = self.get_present_version()

    def get_current_branch(self):
        "Gets the name of the current branch."
        command = "cd \"{name}\" && git symbolic-ref --short HEAD".format(name=self.name)
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE, shell="True", universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        if proc.returncode != 0:
            raise Exception("Could not get name of current branch for {0}".format(self.name))
        print("BRANCH:", stdout)
        return stdout.strip()

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
            self.vif = json.dump(self, viffile, indent="    ")

    def update(self, silent=False):
        for (dep_name, dep_vi) in self.items():
            if not silent: print("Updating", dep_name)
            dep_vi.update()

    def print_version(self, dependency_name):
        try:
            print(self[dependency_name]["version"])
        except:
            print("0.xyz")

def parse_args(test_args=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--file",
        dest="file", type=str, required=True,
        help="Which file to read.")
    argparser.add_argument(
        "--no-update",
        dest="update", default=True, action='store_false',
        help="Do not update dependencies.")
    argparser.add_argument(
        "--output-file",
        dest="out_file", type=str,
        help="Which file to write.")
    argparser.add_argument(
        "--print-version",
        dest="print_version", type=str,
        help="Print just the updated version of the given dependency.")
    return argparser.parse_args(test_args)

def main(test_args=None):
    args = parse_args(test_args)
    current_vif = VersionInformationFile(args.file)
    if args.update:
        current_vif.update(silent=args.print_version is not None)
    if args.print_version is not None:
        current_vif.print_version(args.print_version)
    if args.out_file:
        current_vif.dump(args.out_file)
    return current_vif

if __name__ == "__main__":
    main()
