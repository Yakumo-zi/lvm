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
current_version = cfg.get("current")
installed_versions = cfg.get("installed_versions")
available_versions = cfg.get("versions")


def available():
    global available_versions
    last_update_time = cfg.get("last_update_time")
    if available_versions is None or last_update_time is None or (time.time() - last_update_time) >= 86400//2:
        response = requests.get(config.BASE_URL)
        cfg.set("last_update_time", time.time())
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        available_versions = []
        for link in links:
            link = str(link.get('href'))
            if link.startswith("lua-") and link not in available_versions:
                available_versions.append(link)
        cfg.set("versions", available_versions)
    print("Available versions:")
    for version in [x.replace(".tar.gz", "") for x in available_versions]:
        if current_version == version:
            print("*", version)
            continue
        elif version in installed_versions:
            print("+", version)
            continue
        print(" ", version)
    return available_versions


def get_install_list():
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
    if version in installed_versions:
        shutil.rmtree(Path.joinpath(config.LUA_VERSION_PATH, version))
        installed_versions.remove(version)
        cfg.set("installed_versions", installed_versions)
        if len(installed_versions) != 0:
            if version == current_version:
                use(installed_versions[0])
        else:
            cfg.set("current", "")
        print(f"{version} removed successfully")
    else:
        print(f"{version} is not installed")


def use(version):
    if version not in installed_versions:
        print(f"{version} is not installed")
        return
    if config.CURRENT_USED_VERSION_PATH.is_symlink():
        os.remove(config.CURRENT_USED_VERSION_PATH)
    os.symlink(Path.joinpath(config.LUA_VERSION_PATH,
               version), config.CURRENT_USED_VERSION_PATH)
    cfg.set("current", version)
    print(f"Change lua current version to {version}")


def install(version: str):
    if version in installed_versions:
        print(f"{version} is already installed")
        return
    elif version not in [x.replace(".tar.gz", "") for x in available_versions]:
        print(f"{version} is not available")
        return

    download_specific_version(version)
    install_lua_version(version)
    os.remove(utils.get_lua_version_path(version))
    print(f"type lvm use {version} to use the installed version")


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
    print(f"{version} installed successfully")
    installed_versions.append(version)
    cfg.set("installed_versions", installed_versions)
