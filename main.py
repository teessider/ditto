from pathlib import Path

import ditto

if __name__ == '__main__':

    ditto.make_mock_unreal_install(path=Path.cwd())
    ditto.make_mock_unreal_project(path=Path.cwd())

    test_folders = [
        "FakeUnrealInstall",
        "AFakeFakeUnrealInstallation",
        "ADifferentFakeUnrealInstallation",
        "AnotherAnotherFakeUnrealInstallation"
    ]

    for test_path in test_folders:
        test_install_path = Path.cwd() / test_path

        print(f"Is Unreal Engine Installation ({test_path}): {ditto.is_ue_engine_install(test_install_path)}\n"
              f"Engine Install Path: {test_install_path}")
