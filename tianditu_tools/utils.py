import json
from pathlib import Path
from random import choice

import yaml
from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsSettings

TIANDITU_HOME_URL = "https://www.tianditu.gov.cn/"
PLUGIN_NAME = "tianditu-tools"

PluginDir = Path(__file__).parent

HEADER = {
    "User-Agent": "Mozilla/5.0 QGIS/32400/Windows 10 Version 2009",
    "Referer": "https://www.tianditu.gov.cn/",
}


def get_extramap_status():
    summary = load_yaml(PluginDir.joinpath("maps/summary.yml"))
    default_status = {}
    for section in summary:
        section_data = load_yaml(PluginDir.joinpath(f"maps/{section}.yml"))
        default_status[section] = list(section_data["maps"].keys())
    return default_status


class PluginConfig:
    def __init__(self):
        self.conf = QgsSettings()
        self.conf_name = "tianditu-tools"
        self.section_tianditu = f"{self.conf_name}/Tianditu"

    def init_config(self):
        # 初始化配置文件
        if not self.conf.contains("tianditu-tools/Tianditu/key"):
            print("初始化配置文件")
            # 初始化
            self.conf.setValue(f"{self.section_tianditu}/key", "")
            self.conf.setValue(f"{self.section_tianditu}/keyList", "")
            self.conf.setValue(f"{self.section_tianditu}/random", True)
            self.conf.setValue(f"{self.section_tianditu}/random_key", False)
            self.conf.setValue(f"{self.section_tianditu}/subdomain", "t0")
        if not self.conf.contains("tianditu-tools/Other/extramap_status"):
            print("初始化 extra map 文件")
            self.conf.setValue(
                f"{self.conf_name}/Other/extramap_status", str(get_extramap_status())
            )
        # 升级到保存多个key的版本
        if not self.conf.contains(f"{self.section_tianditu}/keyList"):
            self.conf.setValue(f"{self.section_tianditu}/random_key", False)
            # 保存原来的key
            if self.get_key() != "":
                self.conf.setValue(f"{self.section_tianditu}/keyList", self.get_key())
            else:
                self.conf.setValue(f"{self.section_tianditu}/keyList", "")

    def get_key_list(self):
        data_str = self.get_value("/Tianditu/keyList")
        if data_str == "":
            return []
        return data_str.split(",")

    def save_key_list(self, data_list):
        self.conf.setValue(f"{self.section_tianditu}/keyList", ",".join(data_list))

    def get_extra_maps_status(self):
        data = self.get_value("Other/extramap_status")
        return json.loads(data.replace("'", '"'))

    def set_extra_maps_status(self, data):
        self.conf.setValue(f"{self.conf_name}/Other/extramap_status", str(data))

    def get_value(self, name):
        return self.conf.value(f"{self.conf_name}/{name}")

    def get_bool_value(self, name):
        return self.conf.value(f"{self.conf_name}/{name}", type=bool)

    def set_value(self, name, value):
        self.conf.setValue(f"{self.conf_name}/{name}", value)

    def get_key(self):
        return self.get_value("Tianditu/key")

    def get_random_key(self):
        key_list = self.get_key_list()
        return choice(key_list)

    def set_key(self, key):
        key_to_set = ""
        if key is not None:
            key_to_set = key
        self.conf.setValue(f"{self.section_tianditu}/key", key_to_set)


def make_request(url: str, referer: str = None, params=None):
    u = QUrl(url)
    query = QUrlQuery()
    if params:
        for key, value in params.items():
            query.addQueryItem(key, value)
        u.setQuery(query)
    request = QNetworkRequest(u)
    # request.setHeader(QNetworkRequest.UserAgentHeader, headers["User-Agent"]) # 设置 User-Agent 无效
    if referer:
        request.setRawHeader(b"Referer", referer.encode("utf-8"))

    return request


def tianditu_map_url(maptype: str, token: str, subdomain: str) -> str:
    """
    返回天地图url

    Args:
        maptype (str): 类型
        token (str): 天地图key
        subdomain (str): 使用的子域名

    Returns:
        str: 返回天地图XYZ瓦片地址
    """
    url = f"https://{subdomain}.tianditu.gov.cn/"
    url += (
        f"{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}"
    )
    url += "&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}"
    url += f"&tk={token}"
    return url


def load_yaml(file_path: Path):
    """
    读取YAML文件
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
