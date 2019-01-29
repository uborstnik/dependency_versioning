#!/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import unittest

import tempfile
import subprocess

import yaml

import dependency_versioning as dv

class TestDependencyVersioning(unittest.TestCase):
    def test_read_vif(self):
        "Test reading vifs."
        vif = {
            "pyyaml": {
                "type": "pip",
                "version": "3.13"
            },
            "alpine": {
                "type": "docker",
                "version": "4.0"
            },
            "dependency_versioning": {
                "type": "git",
                "repository": "",
                "version": "1234123412341234123"
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as viffile:
            yaml.dump(vif, viffile)
            viffilename = viffile.name
            viffile.close()
        test_vif = dv.VersionInformationFile(viffilename).get_vif()
        self.assertDictEqual(vif, test_vif)

    def test_get_git_version(self):
        git_dep = dv.GITDependency(name="user_service_manager")
        print(git_dep.get_present_version())

    def test_git_clone(self):
        try:
            (stdout, stderr) = subprocess.Popen("rm -fr user_service_manager", shell=True, universal_newlines=True).communicate()
        except:
            pass
        git_dep = dv.GITDependency(name="user_service_manager", repository="git@hpc-git.ethz.ch:user_service_manager", branch="master")
        git_dep.update()

    def test_git_update(self):
        git_dep = dv.GITDependency(name="user_service_manager", repository="git@hpc-git.ethz.ch:user_service_manager", branch="master")
        git_dep.update()
        print("TEST: HEAD IS AT", git_dep.get_present_version())
        (stdout, stderr) = subprocess.Popen("cd user_service_manager && git reset --hard HEAD^; git status", shell=True, universal_newlines=True).communicate()
        print("TEST: HEAD IS AT", git_dep.get_present_version())
        git_dep.update()
        print("TEST: HEAD IS AT", git_dep.get_present_version())

    def test_git_set_version(self):
        git_dep = dv.GITDependency(name="user_service_manager", repository="git@hpc-git.ethz.ch:user_service_manager", branch="master", version="a7df4b7")
        git_dep.update()
        print("TEST: HEAD IS AT", git_dep.get_present_version())
        
        
if __name__ == "__main__":
    main()
