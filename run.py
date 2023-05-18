import configparser
import shutil
import sys
import zipfile
from pathlib import Path

# Define the source and destination directories
source_dir = Path('.')
dest_dir = source_dir.joinpath('dist/tianditu-tools')

# Define the files to be excluded from copying
exclude_files = ['run.py']

# Other necessary files
other_files = ['metadata.txt', 'PointStyle.qml', 'tianditu.yml', 'extramaps.yml', 'README.md', 'LICENSE']

# Define the command line argument
arg = sys.argv[1] if len(sys.argv) > 1 else None

if arg == 'build':
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    # Create the destination directory if it does not exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_dir_ui = dest_dir.joinpath('ui')
    dest_dir_ui.mkdir(parents=True, exist_ok=True)

    # Copy all .py files from the root directory except for exclude_files
    for file in source_dir.glob('*.py'):
        if file.name not in exclude_files:
            shutil.copy(file, dest_dir)

    # Copy the files listed in other_files to dest_dir
    for file in other_files:
        shutil.copy(source_dir.joinpath(file), dest_dir)

    # Copy all .py files from the ui directory
    for file in source_dir.joinpath('ui').glob('*.py'):
        shutil.copy(file, dest_dir_ui)

    # Copy the entire images directory
    shutil.copytree(source_dir.joinpath('images'), dest_dir.joinpath('images'))

    # Read the metadata.txt file using configparser
    config = configparser.ConfigParser()
    config.read('metadata.txt', encoding='utf-8')

    # Get the version under the [general] section
    version = config.get('general', 'version')

    # Zip the destination directory
    with zipfile.ZipFile(f'{dest_dir}-{version}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in dest_dir.glob('**/*'):
            zipf.write(file, file.relative_to(dest_dir.parent))

    # 删除目标目录
    shutil.rmtree(dest_dir)
    print("完成")

elif arg == 'clean':
    # Remove the destination directory if it exists
    shutil.rmtree(dest_dir.parent, ignore_errors=True)

else:
    print('Invalid argument. Please use "build" or "clean".')
