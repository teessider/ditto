import shutil
from pathlib import Path
import pprint

import ditto

if __name__ == '__main__':

    ditto.make_mock_unreal_install(path=Path.cwd(), name="FakeUnrealInstall")
    ditto.make_mock_unreal_project(path=Path.cwd(), name="FakeUnrealProject")

    # used for testing is_ue_install()
    test_unreal_engine_folders = [
        "FakeUnrealInstall",
        "AFakeFakeUnrealInstallation",
        "ADifferentFakeUnrealInstallation",
        "AnotherAnotherFakeUnrealInstallation",
        "UnrealInstallation"
    ]

    # used for testing is_ue_project()
    test_unreal_project_folders = [
        "FakeUnrealProject",
        "AFakeFakeUnrealProject",
        "ADifferentFakeUnrealProject",
        "AnotherAnotherFakeUnrealProject",
        "UnrealProject"
    ]

    plugins_to_copy: list = []
    dest_project = Path(".")
    copy_ignore = shutil.ignore_patterns("Binaries")

    for test_path in test_unreal_engine_folders:
        test_install_path = Path.cwd() / test_path
        # TODO: Determine how to pick the plugins... (See bool table below...)
        test_marketplace_plugins = ditto.ue_marketplace_plugins(test_install_path)

        print(f"Is Unreal Engine Installation ({test_path}): {ditto.is_ue_engine_install(test_install_path)}\n"
              f"\tEngine Install Path: {test_install_path}\n"
              f"\tNumber of Marketplace Plugins: {len(test_marketplace_plugins)}\n"
              f"\tPlugin Names: {tuple(path.stem for path in test_marketplace_plugins)}")

        if not test_marketplace_plugins:
            continue
        # append simply adds the tuple of plugin paths...so extend() is used here
        plugins_to_copy.extend(test_marketplace_plugins)

    unreal_plugins_to_copy = []
    test_copy_plugins_binaries = [True, False, False]  # These values would come from some UI or other input...
    plugin_to_copy: Path
    for copy_val, plugin_to_copy in enumerate(plugins_to_copy):
        plugin = ditto.UnrealPlugin(root=plugin_to_copy, copy_binaries=test_copy_plugins_binaries[copy_val])
        unreal_plugins_to_copy.append(plugin)

    print(f"{pprint.pformat(unreal_plugins_to_copy)}\n{'_' * 10}")

    for test_path in test_unreal_project_folders:
        test_project_path = Path.cwd() / test_path

        print(f"Is Unreal Project ({test_path}): {ditto.is_ue_project(test_project_path)}\n"
              f"Project Path: {test_project_path}")
        if not ditto.is_ue_project(test_project_path):
            continue
        dest_project = test_project_path

    print(f"Project Path: {dest_project}\n{'_' * 40}")

    dest_project_plugins_path = dest_project / ditto.UE_PLUGINS_FOLDER_NAME
    print(f"Destination: {dest_project_plugins_path}")

    unreal_plugin: ditto.UnrealPlugin
    for unreal_plugin in unreal_plugins_to_copy:
        dest_path = dest_project_plugins_path.joinpath(unreal_plugin.root.stem)
        Path.mkdir(dest_path)

        if unreal_plugin.copy_binaries:
            ditto.copy_ue_plugin(unreal_plugin_path=unreal_plugin.root, dest_path=dest_path,
                                 overwrite_files=True)
        ditto.copy_ue_plugin_no_binaries(unreal_plugin_path=unreal_plugin.root, dest_path=dest_path,
                                         overwrite_files=True)

    # pseudocode:
    # select the plugins
    #   see if it already exists in project?
    #   see what version is there? (also display version in launcher version)
    #   diff them potentially? (there might be local changes)
    #   if local changes...can somehow put them in? or at least put them on clipboard (merge them using merge tool?)
    # see if Binaries folder is wanted to be copied (per plugin)
    # copy the plugin(s)
    #   report errors if not successful
    # compile the plugin(s)?
    # for another engine install....replace the steps for choosing project with engine install
