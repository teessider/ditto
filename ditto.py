from __future__ import annotations

from typing import Optional, Sequence
import json
import os
import shutil
from pathlib import Path
from dataclasses import dataclass

UE_ENGINE_FOLDER_NAME = "Engine"
UE_ENGINE_BUILD_FOLDER_NAME = "Build"
UE_ENGINE_BUILD_VERSION_FILE_NAME = "Build.version"
UE_ENGINE_EDITOR_MODULES_FILE_NAME = "UnrealEditor.modules"

UE_BINARIES_FOLDER_NAME = "Binaries"
UE_PLATFORM_WINDOWS_NAME = "Win64"
UE_PLUGINS_FOLDER_NAME = "Plugins"
UE_MARKETPLACE_PLUGINS_FOLDER_NAME = "Marketplace"
UE_CONFIG_FOLDER_NAME = "Config"
UE_CONTENT_FOLDER_NAME = "Content"
UE_SOURCE_FOLDER_NAME = "Source"
UE_PRIVATE_FOLDER_NAME = "Private"
UE_PUBLIC_FOLDER_NAME = "Public"

UE_UPLUGIN_EXT = "uplugin"
UE_UPROJECT_EXT = "uproject"
UE_CONFIG_EXT = "ini"
UE_CPP_SOURCE_EXT = "cpp"
UE_CPP_HEADER_EXT = "h"
UE_BUILD_CSHARP_EXT = f"{UE_ENGINE_BUILD_FOLDER_NAME}.cs"


@dataclass
class UnrealPlugin:
    root: Path
    copy_binaries: bool
    # plugin_file: TextIO
    # version: float


def create_empty_file(path: os.PathLike) -> None:
    with open(path, "w"):
        pass


def create_unreal_data_file(path: os.PathLike, data: dict,
                            indent: str | int, extra_lines: Optional[str] = None) -> None:
    with open(path, "w") as f:
        json.dump(data, fp=f, indent=indent)
        if extra_lines is not None:
            f.write(extra_lines)


def create_unreal_build_csharp_file(path: os.PathLike, module_name: str) -> None:
    lines = (
        "// Fake Copyright Notice 2024\n",
        "\n",
        "using UnrealBuildTool;\n",
        "\n",
        f"public class {module_name} : ModuleRules\n",
        "{\n",
        f"\tpublic {module_name}(ReadOnlyTargetRules Target) : base (Target)\n",
        "\t{\n",
        "\t\tPCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;\n",
        "\n",
        "\t\tPublicDependencyModuleNames.AddRange(new [] { \"Core\", \"Engine\", \"InputCore\" });\n",
        "\n",
        "\t\tPrivateDependencyModuleNames.AddRange(new [] { \"CoreUObject\", \"RenderCore\" });\n",
        "\t}\n",
        "}\n"
    )
    with open(path, "w") as f:
        f.writelines(lines)


def match_ue_filepath_in_folder(unreal_path: Path, unreal_file_name: str,
                                dirs_to_join: Sequence[str]) -> bool:
    if unreal_path.exists():
        unreal_file_path = unreal_path / unreal_file_name
    else:
        unreal_file_path = unreal_path

    ue_path_pattern = Path("*").joinpath(
        *dirs_to_join,
        unreal_file_name).as_posix()
    return unreal_file_path.match(ue_path_pattern)


def is_ue_engine_install(unreal_install_path: Path) -> bool:
    # How does epic measure what is an Unreal Engine installation "Engine" folder?
    # Engine/Source/Developer/DesktopPlatform/Private/DesktopPlatformBase.cpp#401
    # Epic determines this by checking for Engine/Binaries AND Engine/Build at least for a valid "Root" folder

    engine_path = unreal_install_path / UE_ENGINE_FOLDER_NAME
    engine_binaries_path = engine_path / UE_BINARIES_FOLDER_NAME
    engine_build_path = engine_path / UE_ENGINE_BUILD_FOLDER_NAME

    engine_build_dirs = UE_ENGINE_FOLDER_NAME, UE_ENGINE_BUILD_FOLDER_NAME
    if (engine_binaries_path.exists()
            and match_ue_filepath_in_folder(unreal_path=engine_build_path,
                                            unreal_file_name=UE_ENGINE_BUILD_VERSION_FILE_NAME,
                                            dirs_to_join=engine_build_dirs)):
        return True

    return False


def is_ue_project(unreal_project_path: Path) -> bool:
    uproject_file_name = f"{unreal_project_path.stem}.{UE_UPROJECT_EXT}"

    return match_ue_filepath_in_folder(unreal_path=unreal_project_path, unreal_file_name=uproject_file_name,
                                       dirs_to_join=(unreal_project_path.stem,))


def ue_marketplace_plugins(unreal_install_path: Path) -> tuple | tuple[Path]:
    if not is_ue_engine_install(unreal_install_path):
        return ()
    engine_plugins_path = unreal_install_path / UE_ENGINE_FOLDER_NAME / UE_PLUGINS_FOLDER_NAME
    marketplace_plugins = engine_plugins_path.glob(f"{UE_MARKETPLACE_PLUGINS_FOLDER_NAME}/*/*.{UE_UPLUGIN_EXT}")
    # TODO: return array of UnrealPlugin dataclasses?
    return tuple([plugin_path.parent for plugin_path in marketplace_plugins])


def copy_ue_plugin(unreal_plugin_path: os.PathLike, dest_path: os.PathLike,
                   overwrite_files: bool) -> os.PathLike:
    return shutil.copytree(src=unreal_plugin_path, dst=dest_path,
                           dirs_exist_ok=overwrite_files)


def copy_ue_plugin_no_binaries(unreal_plugin_path: os.PathLike, dest_path: os.PathLike,
                               overwrite_files: bool) -> os.PathLike:
    ignore_pattern = shutil.ignore_patterns("Binaries")
    return shutil.copytree(src=unreal_plugin_path, dst=dest_path, ignore=ignore_pattern,
                           dirs_exist_ok=overwrite_files)


def make_mock_unreal_plugin(path: Path, plugin_name: str) -> None:
    mock_plugin_name = f"{plugin_name}Plugin"
    mock_plugin_editor_module_name = f"{mock_plugin_name}Editor"
    mock_uplugin_data = {
        "FileVersion": 3,
        "Version": 1,
        "VersionName": "1.0",
        "FriendlyName": mock_plugin_name,
        "Description": "Example Engine Marketplace Plugin used for Testing Ditto",
        "Category": "Other",
        "CreatedBy": "Andrew Bell",
        "CreatedByURL": "",
        "DocsURL": "",
        "MarketplaceURL": "",
        "SupportURL": "",
        "CanContainContent": False,
        "IsBetaVersion": False,
        "IsExperimentalVersion": False,
        "Installed": False,
        "Modules": [
            {
                "Name": mock_plugin_name,
                "Type": "Runtime",
                "LoadingPhase": "Default"
            },
            {
                "Name": mock_plugin_editor_module_name,
                "Type": "Editor",
                "LoadingPhase": "Default"
            }
        ]
    }
    mock_editor_modules_data = {
        "BuildId": "27405482",
        "Modules": {
            mock_plugin_name: f"UnrealEditor-{mock_plugin_name}.dll",
            mock_plugin_editor_module_name: f"UnrealEditor-{mock_plugin_editor_module_name}.dll"
        }
    }

    mock_module_build_file_name = f"{mock_plugin_name}.{UE_BUILD_CSHARP_EXT}"
    mock_module_source_file_name = f"{mock_plugin_name}Module.{UE_CPP_SOURCE_EXT}"
    mock_module_header_file_name = f"{mock_plugin_name}Module.{UE_CPP_HEADER_EXT}"
    mock_editor_module_build_file_name = f"{mock_plugin_editor_module_name}.{UE_BUILD_CSHARP_EXT}"
    mock_editor_module_source_file_name = f"{mock_plugin_editor_module_name}Module.{UE_CPP_SOURCE_EXT}"
    mock_editor_module_header_file_name = f"{mock_plugin_editor_module_name}Module.{UE_CPP_HEADER_EXT}"

    mock_plugin_root = path / mock_plugin_name
    mock_uplugin_file_path = mock_plugin_root / f"{mock_plugin_name}.{UE_UPLUGIN_EXT}"
    mock_plugin_binaries_folder = mock_plugin_root / UE_BINARIES_FOLDER_NAME / UE_PLATFORM_WINDOWS_NAME
    mock_editor_modules_path = mock_plugin_binaries_folder / UE_ENGINE_EDITOR_MODULES_FILE_NAME

    mock_plugin_source_folder = mock_plugin_root / UE_SOURCE_FOLDER_NAME
    mock_plugin_module_folder = mock_plugin_source_folder / mock_plugin_name
    mock_plugin_editor_module_folder = mock_plugin_source_folder / mock_plugin_editor_module_name

    mock_module_private_folder = mock_plugin_module_folder / UE_PRIVATE_FOLDER_NAME
    mock_module_public_folder = mock_plugin_module_folder / UE_PUBLIC_FOLDER_NAME
    mock_module_build_cs_path = mock_plugin_module_folder / mock_module_build_file_name
    mock_editor_module_private_folder = mock_plugin_editor_module_folder / UE_PRIVATE_FOLDER_NAME
    mock_editor_module_public_folder = mock_plugin_editor_module_folder / UE_PUBLIC_FOLDER_NAME
    mock_editor_module_build_cs_path = mock_plugin_editor_module_folder / mock_editor_module_build_file_name

    # start making the plugin folder tree structure
    Path.mkdir(mock_plugin_binaries_folder, parents=True)
    create_unreal_data_file(path=mock_editor_modules_path, data=mock_editor_modules_data, indent=4)
    Path.mkdir(mock_module_private_folder, parents=True)
    create_empty_file(path=mock_module_private_folder / mock_module_source_file_name)
    Path.mkdir(mock_module_public_folder)
    create_empty_file(path=mock_module_public_folder / mock_module_header_file_name)
    create_unreal_build_csharp_file(path=mock_module_build_cs_path, module_name=mock_plugin_name)
    Path.mkdir(mock_editor_module_private_folder, parents=True)
    create_empty_file(path=mock_editor_module_private_folder / mock_editor_module_source_file_name)
    Path.mkdir(mock_editor_module_public_folder)
    create_empty_file(path=mock_editor_module_public_folder / mock_editor_module_header_file_name)
    create_unreal_build_csharp_file(path=mock_editor_module_build_cs_path, module_name=mock_plugin_editor_module_name)
    create_unreal_data_file(path=mock_uplugin_file_path, data=mock_uplugin_data, indent="\t")


def make_mock_unreal_install(path: Path, name: str) -> None:
    mock_build_version_data = {
        "MajorVersion": 5,
        "MinorVersion": 3,
        "PatchVersion": 2,
        "Changelist": 0,
        "CompatibleChangelist": 27405482,
        "IsLicenseeVersion": 0,
        "IsPromotedBuild": 0,
        "BranchName": "UE5"
    }
    mock_unreal_editor_modules_data = {
        "BuildId": "27405482",
        "Modules": {
            "ExampleEnginePlugin": "UnrealEditor-ExampleEnginePlugin.dll",
            "ExampleEnginePluginEditor": "UnrealEditor-ExampleEnginePluginEditor.dll"
        }
    }

    mock_unreal_install = path / name

    mock_unreal_engine_folder = mock_unreal_install / UE_ENGINE_FOLDER_NAME
    mock_unreal_binaries_folder = mock_unreal_engine_folder / UE_BINARIES_FOLDER_NAME / UE_PLATFORM_WINDOWS_NAME
    mock_unreal_editor_modules_path = mock_unreal_binaries_folder / UE_ENGINE_EDITOR_MODULES_FILE_NAME

    mock_unreal_build_folder = mock_unreal_engine_folder / UE_ENGINE_BUILD_FOLDER_NAME
    mock_unreal_build_version_path = mock_unreal_build_folder / UE_ENGINE_BUILD_VERSION_FILE_NAME

    mock_unreal_marketplace_plugins_folder = (mock_unreal_engine_folder / UE_PLUGINS_FOLDER_NAME
                                              / UE_MARKETPLACE_PLUGINS_FOLDER_NAME)

    print(f"Fake Unreal Installation Exists: {mock_unreal_install.exists()}\n"
          f"Removing Fake Unreal Installation...")
    shutil.rmtree(mock_unreal_install, ignore_errors=True)
    print(f"Fake Install Exists: {mock_unreal_install.exists()}\n"
          f"{'_' * 10}")

    # Start making the mock installation
    Path.mkdir(mock_unreal_binaries_folder, parents=True)
    Path.mkdir(mock_unreal_build_folder)
    create_unreal_data_file(path=mock_unreal_build_version_path, data=mock_build_version_data, indent="\t",
                            extra_lines="\n\n")
    Path.mkdir(mock_unreal_marketplace_plugins_folder, parents=True)
    create_unreal_data_file(path=mock_unreal_editor_modules_path, data=mock_unreal_editor_modules_data, indent=4)
    make_mock_unreal_plugin(path=mock_unreal_marketplace_plugins_folder, plugin_name="FakeMarketplaceZero")
    make_mock_unreal_plugin(path=mock_unreal_marketplace_plugins_folder, plugin_name="FakeMarketplaceOne")
    make_mock_unreal_plugin(path=mock_unreal_marketplace_plugins_folder, plugin_name="FakeMarketplaceTwo")


def make_mock_unreal_project(path: Path, name: str) -> None:
    mock_uproject_data = {
        "FileVersion": 3,
        "EngineAssociation": "5.3",
        "Category": "",
        "Description": "",
        "Modules": [
            {
                "Name": "EpicExample",
                "Type": "Runtime",
                "LoadingPhase": "Default",
                "AdditionalDependencies": [
                    "Engine"
                ]
            },
            {
                "Name": "EpicExampleEditor",
                "Type": "Editor",
                "LoadingPhase": "PostEngineInit"
            }
        ],
        "Plugins": [
            {
                "Name": "BlankPlugin",
                "Enabled": True
            },
            {
                "Name": "ScriptPlugin",
                "Enabled": True
            }
        ],
        "TargetPlatforms": [
            "Windows"
        ]
    }
    mock_uproject_name = name

    mock_default_editor_config_name = f"DefaultEditor.{UE_CONFIG_EXT}"
    mock_default_engine_config_name = f"Default{UE_ENGINE_FOLDER_NAME}.{UE_CONFIG_EXT}"
    mock_default_game_config_name = f"DefaultGame.{UE_CONFIG_EXT}"

    mock_unreal_project_root = path / mock_uproject_name
    mock_unreal_project_config_folder = mock_unreal_project_root / UE_CONFIG_FOLDER_NAME
    mock_unreal_project_content_folder = mock_unreal_project_root / UE_CONTENT_FOLDER_NAME
    mock_unreal_project_plugins_folder = mock_unreal_project_root / UE_PLUGINS_FOLDER_NAME
    mock_unreal_project_file_path = mock_unreal_project_root / f"{mock_uproject_name}.{UE_UPROJECT_EXT}"

    print(f"Fake Unreal Project Exists: {mock_unreal_project_root.exists()}\n"
          f"Removing Fake Unreal Project...")
    shutil.rmtree(mock_unreal_project_root, ignore_errors=True)
    print(f"Fake Project Exists: {mock_unreal_project_root.exists()}\n"
          f"{'_' * 10}")

    # Start making the mock unreal project
    Path.mkdir(mock_unreal_project_config_folder, parents=True)
    create_empty_file(path=mock_unreal_project_config_folder / mock_default_editor_config_name)
    create_empty_file(path=mock_unreal_project_config_folder / mock_default_engine_config_name)
    create_empty_file(path=mock_unreal_project_config_folder / mock_default_game_config_name)
    Path.mkdir(mock_unreal_project_plugins_folder)
    create_unreal_data_file(path=mock_unreal_project_file_path, data=mock_uproject_data, indent="\t")
    Path.mkdir(mock_unreal_project_content_folder)
