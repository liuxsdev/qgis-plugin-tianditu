from pathlib import Path
import shutil
import sys
import zipfile

# 获取命令行参数
args = sys.argv[1:]

# 定义源目录和目标目录
source_dir = Path('.')
target_dir = source_dir.joinpath('dist/tianditu-tools')

# 如果命令行参数为build，则复制文件
if 'build' in args:
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    # 复制.py文件、metadata.txt、PointStyle.qml、icon.png
    for file in source_dir.glob('*.py'):
        shutil.copy(file, target_dir)
    shutil.copy('metadata.txt', target_dir)
    shutil.copy('PointStyle.qml', target_dir)
    shutil.copy('icon.png', target_dir)
    
    # 复制ui目录下的所有文件
    ui_dir_target = target_dir.joinpath('ui')
    ui_dir_target.mkdir(parents=True, exist_ok=True)
    ui_dir = source_dir.joinpath('ui')
    for file in ui_dir.glob('*.py'):
        shutil.copy(file, ui_dir_target)
    
    # 复制images目录下的所有文件
    images_dir = source_dir / 'images'
    images_dir_target = target_dir.joinpath('images')
    images_dir_target.mkdir(parents=True, exist_ok=True)
    for file in images_dir.glob('*'):
        shutil.copy(file, images_dir_target)
    
    # 压缩目标目录为zip文件
    with zipfile.ZipFile(target_dir.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in target_dir.glob('**/*'):
            zipf.write(file, file.relative_to(target_dir.parent))
    
    # 删除目标目录
    shutil.rmtree(target_dir)
    print("完成")

# 如果命令行参数为clean，则清除目标目录
elif 'clean' in args:
    if target_dir.parent.exists:
        shutil.rmtree(target_dir.parent)
        print("清除 dist 目录")
# 如果命令行参数不是build或clean，则输出错误信息
else:
    print('Invalid argument. Please use "build" or "clean".')