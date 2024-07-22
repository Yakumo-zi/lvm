from pathlib import Path
from typing import Optional
import json
import os
BASE_URL = "https://www.lua.org/ftp/"
EXTENSION = ".tar.gz"
LUA_VERSION_PATH = Path.joinpath(Path.home(), ".lvm")
CURRENT_USED_VERSION_PATH = Path.joinpath(LUA_VERSION_PATH, "current")
CONFIG_PATH = Path.joinpath(LUA_VERSION_PATH, "config.json")

BIN = ["lua", "luac"]
INCLUDE = ["lauxlib.h", "lua.h", "luaconf.h", "lualib.h"]
LIB = ["liblua.a"]
need_to_install = {
    "bin": BIN,
    "include": INCLUDE,
    "lib": LIB,
}


class Config():
    def __init__(self):
        if not LUA_VERSION_PATH.exists():
            os.makedirs(LUA_VERSION_PATH)
        self.path = CONFIG_PATH
        self.data = {
            "versions": [],
            "last_update_time": None,
            "current": None,
            "installed_versions": []
        }
        if not self.path.exists():
            self.path.touch()
            with open(self.path, 'w') as f:
                json.dump(self.data, f)
        else:
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        self.init_installed_versions()

    def init_installed_versions(self):
        self.data["installed_versions"] = []
        for version in os.listdir(LUA_VERSION_PATH):
            if version != "current" and version != "config.json":
                if os.path.isdir(Path.joinpath(LUA_VERSION_PATH, version)):
                    self.data["installed_versions"].append(version)
        json.dump(self.data, open(self.path, 'w'))

    def get(self, key) -> Optional[str]:
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

    def remove(self, key):
        del self.data[key]
        with open(self.path, 'w') as f:
            json.dump(self.data, f)


cfg = Config()
