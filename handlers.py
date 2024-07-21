import config
import shutil
import tarfile
import os
from pathlib import Path
import subprocess
import utils
import time
import requests
from bs4 import BeautifulSoup
cfg = config.cfg


def available():
    versions: [str] = cfg.get("versions")
    last_update_time = cfg.get("last_update_time")
    if versions is not None and last_update_time is not None:
        if (time.time() - last_update_time) < 86400//2:
            return versions
    response = requests.get(config.BASE_URL)
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


def get_install_list():
    installed_versions: [str] = cfg.get("installed_versions")
    current_version = cfg.get("current")
    if len(installed_versions) == 0:
        print("No lua versions installed")
    else:
        for version in installed_versions:
            if version == current_version:
                print(f"* {version}")
                continue
            print(f"  {version}")


def shell_init(shell: str):
    if shell == "bash":
        print(f"export PATH=$PATH:{config.CURRENT_USED_VERSION_PATH}/bin")
    elif shell == "zsh":
        print(f"export PATH=$PATH:{config.CURRENT_USED_VERSION_PATH}/bin")
    else:
        print("Unsupported shell")


def uninstall(version):
    if version in cfg.get("installed_versions"):
        shutil.rmtree(Path.joinpath(config.LUA_VERSION_PATH, version))
        cfg.get("installed_versions").remove(version)
        cfg.set("installed_versions", cfg.get("installed_versions"))
        print(f"Lua {version} removed successfully")
    else:
        print(f"Lua {version} is not installed")


def use(version):
    if config.CURRENT_USED_VERSION_PATH.exists():
        os.remove(config.CURRENT_USED_VERSION_PATH)
    os.symlink(Path.joinpath(config.LUA_VERSION_PATH,
               version), config.CURRENT_USED_VERSION_PATH)
    cfg.set("current", version)
    print(f"Change lua current version to {version}")


def install(version: str):
    download_specific_version(version)
    install_lua_version(version)


def download_specific_version(version: str):
    current_version_path = utils.get_lua_version_path(version)
    url = config.BASE_URL + version+config.EXTENSION
    response = requests.get(url, stream=True)
    with open(current_version_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
    with tarfile.open(current_version_path) as tar:
        tar.extractall(config.LUA_VERSION_PATH)


def install_lua_version(version):
    installed_versions: [str] = cfg.get("installed_versions")
    if version not in installed_versions:
        installed_versions.append(version)
        cfg.set("installed_versions", installed_versions)
        devNULL = open(os.devnull, 'wb')
        path = Path.joinpath(config.LUA_VERSION_PATH, version)
        subprocess.run(["make", "linux"], cwd=path, stdout=devNULL)
        for k, v in config.need_to_install.items():
            os.makedirs(Path.joinpath(
                config.LUA_VERSION_PATH, version, k), exist_ok=True)
            utils.copy_files_to_dir(
                v, Path.joinpath(config.LUA_VERSION_PATH, version, k), version)
        subprocess.run(["rm", "-rf", "doc", "Makefile",
                        "src", "README"], cwd=path, stdout=devNULL)
        print(f"Lua {version} installed successfully")
    else:
        print(f"Lua {version} already installed")
