import configparser
import shutil
import sys
import zipfile
from pathlib import Path

# Define the source and destination directories
cwd = Path.cwd()
source_dir = cwd.joinpath("tianditu-tools")
dist_dir = cwd.joinpath("dist")
dist_source_dir = dist_dir.joinpath("tianditu-tools")

# Other necessary files
other_files = ["README.md", "LICENSE"]

# Define the command line argument
arg = sys.argv[1] if len(sys.argv) > 1 else None

if arg == "build":
    if dist_source_dir.exists():
        shutil.rmtree(dist_source_dir)
    # 复制源文件夹到dist目录下的tianditu-tools文件夹
    shutil.copytree(source_dir, dist_source_dir)

    # 删除ui文件夹的ui文件，只保留python文件
    for file_path in dist_source_dir.joinpath("ui").glob("*.ui"):
        file_path.unlink()
    # 复制README和LICENSE文件
    for file in other_files:
        shutil.copy(cwd.joinpath(file), dist_source_dir)

    # Read the metadata.txt file using configparser
    config = configparser.ConfigParser()
    config.read(source_dir.joinpath("metadata.txt"), encoding="utf-8")

    # Get the version under the [general] section
    version = config.get("general", "version")

    filename = f"tianditu-tools-{version}.zip"

    # Zip the destination directory
    with zipfile.ZipFile(
        dist_dir.joinpath(filename), "w", zipfile.ZIP_DEFLATED
    ) as zipf:
        for file in dist_source_dir.glob("**/*"):
            zipf.write(file, file.relative_to(dist_source_dir.parent))

    # 删除dist目录
    shutil.rmtree(dist_source_dir)
    print(f"完成打包 {filename}")

elif arg == "clean":
    # Remove the destination directory if it exists
    shutil.rmtree(dist_dir, ignore_errors=True)

else:
    print('Invalid argument. Please use "build" or "clean".')
