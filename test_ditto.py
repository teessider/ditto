from unittest import TestCase
from pathlib import Path
from typing import Sequence
from collections import Iterable

import ditto

# TODO:
#  turn into Test Suite with:
#  - making mock unreal install
#  - making mock unreal project
#  - test ditto.match_ue_filepath_in_folder?
#  - test ditto.ue_marketplace_plugins?
#  - test ditto.copy_ue_plugin?
#  - test ditto.copy_ue_plugin_no_binaries

class TestIsUEEnvironment(TestCase):

    def setUp(self):
        self.install_suffix = "Install"
        self.test_engine_folders = (
            f"FakeUnreal{self.install_suffix}",
            f"AFakeFakeUnreal{self.install_suffix}",
            f"ADifferentFakeUnreal{self.install_suffix}",
            f"AnotherAnotherFakeUnreal{self.install_suffix}",
            f"Unreal{self.install_suffix}"
        )
        self.project_suffix = "Project"
        self.test_project_folders = (
            f"FakeUnreal{self.project_suffix}",
            f"AFakeFakeUnreal{self.project_suffix}",
            f"ADifferentFakeUnreal{self.project_suffix}",
            f"AnotherAnotherFakeUnreal{self.project_suffix}",
            f"Unreal{self.project_suffix}"
        )

    def tearDown(self):
        self.test_engine_folders = None
        self.test_project_folders = None

    def is_ue_env_test(self, test_folders: Sequence[str], test_pass_folder: str, func) -> None:
        test_folder: str
        for test_folder in test_folders:
            ue_env_folder = Path.cwd() / test_folder
            if test_folder != test_pass_folder:
                self.assertFalse(func(ue_env_folder))
                continue
            self.assertTrue(func(ue_env_folder))

    def match_ue_env_pattern_test(self, root: Path, file_name: str, folders_to_join: Sequence[str]):
        self.assertIsInstance(root, Path)
        self.assertIsInstance(file_name, str)
        self.assertIsInstance(folders_to_join, Iterable)
        match_test = ditto.match_ue_filepath_in_folder(
            unreal_path=root,
            unreal_file_name=file_name,
            dirs_to_join=folders_to_join)
        self.assertIsInstance(match_test, bool)
        self.assertTrue(match_test)

    def test_match_ue_engine_install_pattern(self):
        engine_build_path = Path(Path.cwd() / self.test_engine_folders[0] /
                                 ditto.UE_ENGINE_FOLDER_NAME / ditto.UE_ENGINE_BUILD_FOLDER_NAME)
        engine_build_dirs = ditto.UE_ENGINE_FOLDER_NAME, ditto.UE_ENGINE_BUILD_FOLDER_NAME

        self.match_ue_env_pattern_test(
            root=engine_build_path,
            file_name=ditto.UE_ENGINE_BUILD_VERSION_FILE_NAME,
            folders_to_join=engine_build_dirs)

    def test_match_ue_project_pattern(self):
        project_path = Path.cwd() / self.test_project_folders[0]
        uproject_file_name = f"{project_path.stem}.{ditto.UE_UPROJECT_EXT}"
        project_folders = (project_path.stem, )

        self.match_ue_env_pattern_test(
            root=project_path,
            file_name=uproject_file_name,
            folders_to_join=project_folders)

    def test_is_ue_engine_install(self):
        self.is_ue_env_test(test_folders=self.test_engine_folders,
                            test_pass_folder=self.test_engine_folders[0],
                            func=ditto.is_ue_engine_install)

    def test_is_ue_project(self):
        self.is_ue_env_test(test_folders=self.test_project_folders,
                            test_pass_folder=self.test_project_folders[0],
                            func=ditto.is_ue_project)
