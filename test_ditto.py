from unittest import TestCase
from pathlib import Path
import ditto

# TODO:
#  turn into Test Suite with:
#  - making mock unreal install
#  - making mock unreal project
#  - test ditto.match_ue_filepath_in_folder?
#  - test ditto.ue_marketplace_plugins?
#  - test ditto.copy_ue_plugin?
#  - test ditto.copy_ue_plugin_no_binaries

class TestIsUEEngineInstall(TestCase):

    def setUp(self):
        self.test_engine_folders = [
            "FakeUnrealInstall",
            "AFakeFakeUnrealInstallation",
            "ADifferentFakeUnrealInstallation",
            "AnotherAnotherFakeUnrealInstallation",
            "UnrealInstallation"
        ]

    def test_is_ue_engine_install(self):
        for test_folder in self.test_engine_folders:
            install_folder = Path.cwd() / test_folder
            if test_folder != "FakeUnrealInstall":
                self.assertFalse(ditto.is_ue_engine_install(install_folder))
                continue
            self.assertTrue(ditto.is_ue_engine_install(install_folder))


class TestIsUEProject(TestCase):

    def setUp(self):
        self.unreal_project_folders = [
            "FakeUnrealProject",
            "AFakeFakeUnrealProject",
            "ADifferentFakeUnrealProject",
            "AnotherAnotherFakeUnrealProject",
            "UnrealProject"
        ]

    def test_is_ue_project(self):
        for test_folder in self.unreal_project_folders:
            project_folder = Path.cwd() / test_folder
            if test_folder != "FakeUnrealProject":
                self.assertFalse(ditto.is_ue_project(project_folder))
                continue
            self.assertTrue(ditto.is_ue_project(project_folder))
