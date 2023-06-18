# TianDiTu Tools

[![Version](https://img.shields.io/badge/dynamic/xml?color=blue&label=Version&query=%2F%2Fpyqgis_plugin%5B%40name%3D%27TianDiTu%20Tools%27%5D%2Fversion%2Ftext%28%29&url=https%3A%2F%2Fplugins.qgis.org%2Fplugins%2Fplugins.xml%3Fqgis%3D3.30)](https://plugins.qgis.org/plugins/tianditu-tools/)
[![Downloads](https://img.shields.io/badge/dynamic/xml?color=success&label=Downloads&query=%2F%2Fpyqgis_plugin%5B%40name%3D%27TianDiTu%20Tools%27%5D%2Fdownloads%2Ftext%28%29&url=https%3A%2F%2Fplugins.qgis.org%2Fplugins%2Fplugins.xml%3Fqgis%3D3.30)](https://plugins.qgis.org/plugins/tianditu-tools/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

QGIS 天地图工具，方便进行天地图瓦片底图的添加以及简单实现了部分[天地图 Web 服务 API](http://lbs.tianditu.gov.cn/server/guide.html)（地名搜索、地理编码查询、逆地理编码查询）

## 使用说明

安装插件后，可在 QGIS 工具栏中看到工具按钮，按钮功能分别为添加底图、搜索、以及设置

### 设置天地图 Key

使用前需要设置天地图 Key，点击设置按钮，输入 key，保存并检查

> 天地图 key 需要到[ 天地图控制台 ](https://console.tianditu.gov.cn/api/key)去申请，申请的类型为“浏览器端”

![设置](doc/设置.webp)

### 天地图底图添加

在工具栏下拉菜单中选择底图，点击即可添加到当前工程中。

![工具栏界面](doc/菜单.png)

### 天地图 Web 服务 API

|            地名搜索            |                地理编码                |                 逆地理编码                 |
| :----------------------------: | :------------------------------------: | :----------------------------------------: |
| ![地名搜索](doc/地名搜索.webp) | ![地理编码查询](doc/地理编码查询.webp) | ![逆地理编码查询](doc/逆地理编码查询.webp) |

双击结果项(或点击链接)可添加至当前地图中：

![地点标记](doc/地点标记.webp)
