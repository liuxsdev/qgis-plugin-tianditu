import configparser
import shutil
import zipfile
from pathlib import Path

# Define the source and destination directories
cwd = Path.cwd()
source_dir = cwd.joinpath("tianditu_tools")
dist_dir = cwd.joinpath("dist")
dist_source_dir = dist_dir.joinpath("tianditu-tools")  # same as original plugin package name (tianditu-tools).

# Other necessary files
other_files = ["README.md", "LICENSE"]


def delete_pycache(directory):
    pycache_dir = directory.joinpath("__pycache__")

    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    for subdirectory in directory.iterdir():
        if subdirectory.is_dir():
            delete_pycache(subdirectory)


# 删除dist文件夹
if dist_dir.exists():
    shutil.rmtree(dist_dir)
# 递归删除 __pycache__ 文件夹
delete_pycache(source_dir)
# 复制源文件夹到 dist 目录下的 ianditu-tools 文件夹
shutil.copytree(source_dir, dist_source_dir)
# 删除ui文件夹的 ui 文件，只保留 python 文件
for file_path in dist_source_dir.joinpath("ui").glob("*.ui"):
    file_path.unlink()
# 复制 README 和 LICENSE 文件
for file in other_files:
    shutil.copy(cwd.joinpath(file), dist_source_dir)
# Read the metadata.txt file using configparser
config = configparser.ConfigParser()
config.read(source_dir.joinpath("metadata.txt"), encoding="utf-8")
# Get the version under the [general] section
version = config.get("general", "version")
filename = f"tianditu_tools-{version}.zip"
# Zip the destination directory
with zipfile.ZipFile(dist_dir.joinpath(filename), "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in dist_source_dir.glob("**/*"):
        zipf.write(file, file.relative_to(dist_source_dir.parent))
# 删除dist下的打包目录 tianditu_tools
shutil.rmtree(dist_source_dir)
print(f"完成打包 {filename}")
