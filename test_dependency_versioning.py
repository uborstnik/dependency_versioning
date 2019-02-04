#!/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import unittest

import tempfile
import subprocess
import os

import yaml

import dependency_versioning as dv

def mktempdir():
    tempdir = tempfile.TemporaryDirectory()
    tempdir_name = self.tempdir.name
    subprocess.Popen(
        "OD=$PWD&&cd {dir:s}&&tar xzf $OD/test_repo.tgz".format(dir=self.tempdir_name),
        shell="True", universal_newlines=True).communicate()
    return (tempdir)

def rmtempdir(tempdir):
    tempdir.cleanup()

class TestDependencyVersioning(unittest.TestCase):
    def test_read_vif(self):
        "Test reading vifs."
        vif = {
            "test": {
                "type": "git",
                "repository": "nowhere",
                "branch": "master",
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as viffile:
            yaml.dump(vif, viffile)
            viffilename = viffile.name
            viffile.close()
        test_vif = dv.VersionInformationFile(viffilename).get_vif()
        self.assertDictEqual(vif, test_vif)


class TestGITDependencyVersioning(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.tempdir_name = self.tempdir.name
        subprocess.Popen(
            "OD=$PWD&&cd {dir:s}&&tar xzf $OD/test_repo.tgz".format(dir=self.tempdir_name),
            shell="True", universal_newlines=True).communicate()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_get_git_version(self):
        git_dep = dv.GITDependency(name="user_service_manager", version_info={})
        print(git_dep.get_present_version())

    def test_git_clone(self):
        try:
            (stdout, stderr) = subprocess.Popen("rm -fr test_repo", shell=True, universal_newlines=True).communicate()
        except:
            pass
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "master"})
        git_dep.update()

    def test_git_update(self):
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "master"})
        git_dep.update()
        self.assertEqual(git_dep.get_present_version(), "4cc3b223d2997c8bbf84bfeae420b0d1e4dad732")
        (stdout, stderr) = subprocess.Popen("cd test_repo && git reset --hard HEAD^", shell=True, universal_newlines=True).communicate()
        self.assertEqual(git_dep.get_present_version(), "395c738b6aa8b7074d7d2e533c95276cc0990876")
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "master"})
        git_dep.update()
        self.assertEqual(git_dep.get_present_version(), "4cc3b223d2997c8bbf84bfeae420b0d1e4dad732")

    def test_git_change_branch(self):
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "master"})
        git_dep.update()
        self.assertEqual(git_dep.get_present_version(), "4cc3b223d2997c8bbf84bfeae420b0d1e4dad732")
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "dev"})
        git_dep.update()
        self.assertEqual(git_dep.get_present_version(), "238aacacf8d4c0a73f3395912c5114763fa195ab")

    def test_git_set_version(self):
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "master"})
        git_dep.update()
        self.assertEqual(git_dep.get_present_version(), "4cc3b223d2997c8bbf84bfeae420b0d1e4dad732")
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": os.path.join(self.tempdir_name, "test_repo"),
                "branch": "master",
                "version": "395c738b6aa8b7074d7d2e533c95276cc0990876"})
        git_dep.update()
        self.assertEqual(git_dep.get_present_version(), "395c738b6aa8b7074d7d2e533c95276cc0990876")

    def test_git_get_info(self):
        repo = os.path.join(self.tempdir_name, "test_repo")
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": repo,
                "branch": "master",
                "version": "395c738b6aa8b7074d7d2e533c95276cc0990876"})
        git_dep = dv.GITDependency(
            name="test_repo",
            version_info = {
                "repository": repo,
                "branch": "master"})
        git_dep.update()
        self.assertDictEqual(
            git_dep.get_present_info(),
            {
                "type": "git",
                "repository": repo,
                "branch": "master",
                "version": "4cc3b223d2997c8bbf84bfeae420b0d1e4dad732"
            }
        )
        self.assertDictEqual(
            git_dep,
            {
                "type": "git",
                "repository": repo,
                "branch": "master",
                "version": "4cc3b223d2997c8bbf84bfeae420b0d1e4dad732"
            }
        )

if __name__ == "__main__":
    main()
