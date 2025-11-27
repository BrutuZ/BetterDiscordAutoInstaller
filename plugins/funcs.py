import logging
import re

import requests

from plugins.classes import *
from utils.update import is_version_greater

logger = logging.getLogger("plugins")


def read_plugin_version(input: list[str]):
    for line in input:
        if "@version" in line:
            match = re.search(r"[\d.]+", line)
            if match:
                return match.group()
    return "0.0"


def download_plugin(plugin_info: PluginInfo):
    plugin_dir = os.path.dirname(plugin_info.save_path)
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)

    try:
        logger.debug(f"Downloading {plugin_info.get_name()}...")

        response = requests.get(plugin_info.url)
        if response.status_code != 200:
            logger.error(f"Failed to download plugin from {plugin_info.url}: {response.status_code}")
            return
    except Exception as e:
        logger.error(f"An error occurred while downloading the plugin: {e}")

    if plugin_info.is_installed():
        with open(plugin_info.save_path, encoding="utf-8") as file:
            plugin_version = read_plugin_version(file.readlines())
        logger.info(f"{plugin_info.get_name()} v{plugin_version} installed.")
    else:
        plugin_version = "0.0"

    remote_version = read_plugin_version(response.text.splitlines())
    if is_version_greater(remote_version, plugin_version):
        logger.info(f"Installing plugin {plugin_info.get_name()} v{remote_version}")
        with open(plugin_info.save_path, "wb") as plugin_file:
            plugin_file.write(response.content)
