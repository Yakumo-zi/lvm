import shutil
import config
from pathlib import Path


def copy_files_to_dir(files: list, dest_dir: Path, version: str):
    source_dir = Path.joinpath(config.LUA_VERSION_PATH, version, "src")
    for file in files:
        shutil.copy(Path.joinpath(source_dir, file), dest_dir)


def get_lua_version_path(version):
    return Path.joinpath(config.LUA_VERSION_PATH, version+config.EXTENSION)
