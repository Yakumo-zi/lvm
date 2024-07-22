from pathlib import Path
import shutil
import config
from wasabi import Printer

msg = Printer()
star = msg.text("*", color="green", no_print=True)
plus = msg.text("+", color="cyan", no_print=True)


def copy_files_to_dir(files: list, dest_dir: Path, version: str):
    source_dir = Path.joinpath(config.LUA_VERSION_PATH, version, "src")
    for file in files:
        shutil.copy(Path.joinpath(source_dir, file), dest_dir)


def get_lua_version_path(version):
    return Path.joinpath(config.LUA_VERSION_PATH, version+config.EXTENSION)


def get_color_text(text: str, color: str) -> str:
    return msg.text(text, color=color, no_print=True)
