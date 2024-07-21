#!/home/tohsaka/.version-fox/temp/1721491200-1128/python/bin/python
import requests
import os
import shutil
import time
import json
from typing import Optional
from pathlib import Path
import tarfile
from bs4 import BeautifulSoup
import subprocess
import sys

BASE_URL = "https://www.lua.org/ftp/"
EXTENSION = ".tar.gz"
LUA_VERSION_PATH = Path.joinpath(Path.home(), ".lvm")
CURRENT_VERSION_PATH = Path.joinpath(LUA_VERSION_PATH, "current")
CONFIG_PATH = Path.joinpath(LUA_VERSION_PATH, "config.json")


class config():
    def __init__(self):
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


cfg = config()


def get_lua_versions():
    versions: [str] = cfg.get("versions")
    last_update_time = cfg.get("last_update_time")
    if versions is not None and last_update_time is not None:
        if (time.time() - last_update_time) < 86400//2:
            return versions
    response = requests.get(BASE_URL)
    cfg.set("last_update_time", time.time())
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    versions = []
    for link in links:
        link = str(link.get('href'))
        if link.startswith("lua-") and link not in versions:
            versions.append(link)
    cfg.set("versions", versions)
    return versions


def get_lua_version_path(version):
    return Path.joinpath(LUA_VERSION_PATH, version+EXTENSION)


def download_lua(version):
    url = BASE_URL + version+EXTENSION
    response = requests.get(url, stream=True)
    with open(get_lua_version_path(version), 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)


def extract_tar_gz(file_path, extract_path):
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(path=extract_path)
        print(f'Extracted {file_path} to {extract_path}')


def make_verion_lua(version):
    installed_versions: [str] = cfg.get("installed_versions")
    if version not in installed_versions:
        installed_versions.append(version)
        cfg.set("installed_versions", installed_versions)
        devNULL = open(os.devnull, 'wb')
        path = Path.joinpath(LUA_VERSION_PATH, version)
        subprocess.run(["make", "linux"], cwd=path, stdout=devNULL)
        subprocess.run(["cp", "./src/lua", "./src/luac", "."],
                       cwd=path, stdout=devNULL)
        subprocess.run(["rm", "-rf", "doc", "Makefile",
                        "src", "README"], cwd=path, stdout=devNULL)
        print(f"Lua {version} installed successfully")
    else:
        print(f"Lua {version} already installed")


def use_lua_version(version):
    set_current_version(version)


def remove_lua_version(version):
    if version in cfg.get("installed_versions"):
        shutil.rmtree(Path.joinpath(LUA_VERSION_PATH, version))
        cfg.get("installed_versions").remove(version)
        cfg.set("installed_versions", cfg.get("installed_versions"))
        print(f"Lua {version} removed successfully")
    else:
        print(f"Lua {version} is not installed")


def set_current_version(version):
    if CURRENT_VERSION_PATH.exists():
        os.remove(CURRENT_VERSION_PATH)
    os.symlink(Path.joinpath(LUA_VERSION_PATH, version), CURRENT_VERSION_PATH)
    cfg.set("current", version)
    print(f"Change lua current version to {version}")


if __name__ == "__main__":
    if not LUA_VERSION_PATH.exists():
        os.makedirs(LUA_VERSION_PATH)
    versions = [version.replace(EXTENSION, "")
                for version in get_lua_versions()]
    current_verion = cfg.get("current")
    installed_versions = cfg.get("installed_versions")
    if current_verion is not None:
        print(f"Current version: {current_verion}")
    else:
        print("Any version of Lua has been installed")
    if len(sys.argv) > 1:
        if sys.argv[1] == "version":
            print("Available versions:")
            for version in versions:
                if current_verion == version:
                    print("*", version)
                    continue
                elif version in installed_versions:
                    print("+", version)
                    continue
                print(" ", version)
        elif sys.argv[1] == "download":
            if (len(sys.argv) < 3):
                print("Usage: python main.py download <version>")
                sys.exit(1)
            version = sys.argv[2]
            if version in versions and not Path.joinpath(LUA_VERSION_PATH, version).exists():
                download_lua(version)
                print("file download successfully")
                extract_tar_gz(get_lua_version_path(version), LUA_VERSION_PATH)
                make_verion_lua(version)
                os.remove(get_lua_version_path(version))
                set_current_version(version)
            else:
                print("Invalid version or version already exists")
        elif sys.argv[1] == "init":
            if (len(sys.argv) < 3):
                print("Usage: python main.py init <shell>")
            elif (len(sys.argv) == 3):
                print("export PATH=$PATH:"+str(CURRENT_VERSION_PATH))
        elif sys.argv[1] == "list":
            print("Installed versions:")
            for version in installed_versions:
                if current_verion == version:
                    print("*", version)
                    continue
                print(" ", version)
        elif sys.argv[1] == "use":
            if (len(sys.argv) < 3):
                print("Usage: python lvm.py use <version>")
                sys.exit(1)
            version = sys.argv[2]
            if version in installed_versions:
                use_lua_version(version)
            else:
                print(f"The version:{sys.argv[2]} is not installed")
        elif sys.argv[1] == "remove":
            if (len(sys.argv) < 3):
                print("Usage: python lvm.py remove <version>")
                sys.exit(1)
            version = sys.argv[2]
            remove_lua_version(version)
        elif sys.argv[1] == "help":
            print("Usage: python lvm.py <cmd>")
            print("  Available commands:")
            print("    version: list available versions")
            print("    download <version>: download and install lua version,'+' means installed version, '*' means current version")
            print("    init <shell>: initialize lua version")
            print("    list: list installed versions")
            print("    use <version>: use lua version")
            print("    remove <version>: remove lua version")

    else:
        print("Usage: python lvm.py <cmd>")
        print("  Available commands:")
        print("    version: list available versions")
        print("    download <version>: download and install lua version,'+' means installed version, '*' means current version")
        print("    init <shell>: initialize lua version")
        print("    list: list installed versions")
        print("    use <version>: use lua version")
        print("    remove <version>: remove lua version")
