import yaml
import os
from .utils import PluginDir

EXTRAMAPS_PATH = os.path.join(PluginDir, "extramaps.yml")
with open(EXTRAMAPS_PATH, encoding="utf-8") as f:
    extra_maps = yaml.load(f, Loader=yaml.FullLoader)

T_PATH = os.path.join(PluginDir, "tianditu.yml")
with open(T_PATH, encoding="utf-8") as f:
    tianditu_province = yaml.load(f, Loader=yaml.FullLoader)

TianMapInfo = {
    "vec": "天地图-矢量底图",
    "cva": "天地图-矢量注记",
    "img": "天地图-影像底图",
    "cia": "天地图-影像注记",
    "ter": "天地图-地形晕染",
    "cta": "天地图-地形注记",
    "eva": "天地图-英文矢量注记",
    "eia": "天地图-英文影像注记",
    "ibo": "天地图-全球境界",
}
