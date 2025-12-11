import logging
import re

import requests

from plugins.classes import *
from utils.update import is_version_greater

logger = logging.getLogger("plugins")


def read_plugin_version(input: str):
    match = re.search(r"@version\s+([\d.]+)", input)
    if match:
        return match.group(1)
    return "0"


def download_plugin(plugin_info: PluginInfo):
    installed_version = "0"
    remote_version = "0"
    if plugin_info.is_installed():
        with open(plugin_info.save_path, encoding="utf-8") as file:
            for line in file:
                installed_version = read_plugin_version(line)
                if installed_version != "0":
                    logger.info(f"... v{installed_version} installed.")
                    break

    plugin_dir = os.path.dirname(plugin_info.save_path)
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)

    try:
        logger.debug(f"... Downloading {plugin_info.get_name()}...")
        with requests.get(plugin_info.url, stream=True) as response:
            if not response.ok:
                logger.error(f"... Failed to download plugin from {plugin_info.url}: {response.status_code}")
                return None

            if response.encoding is None:
                response.encoding = "utf-8"

            lines = []
            for line in response.iter_lines():
                lines.append(line)
                if remote_version == "0":
                    remote_version = read_plugin_version(line.decode("utf-8"))
                elif remote_version == installed_version:
                    logger.info("... Already up to date")
                    response.close()
                    return None
                elif not is_version_greater(remote_version, installed_version):
                    logger.info(f"... Installed version (v{installed_version}) isn't older than remote (v{remote_version})")
                    response.close()
                    return None

            logger.info(f"... Installing v{remote_version}")
            with open(plugin_info.save_path, "wb") as plugin_file:
                plugin_file.write(b"\n".join(lines))

    except requests.RequestException as e:
        logger.error(f"An error occurred while downloading the plugin: {e}")
        return None
