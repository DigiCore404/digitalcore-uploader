"""Explicit legacy directory staging for command-line uploads."""
import os, shutil
from pathlib import Path

def stage(value, config, mode):
    source=Path(value).expanduser().resolve(strict=True)
    if not source.is_dir():raise ValueError('Directory staging requires a release folder.')
    root=Path(config.get('Paths','DATADIR')).resolve(strict=True)
    if source.is_relative_to(root):return str(source)
    target=root/source.name
    if target.exists() or target.is_symlink():raise ValueError('A release with this name already exists. Nothing was overwritten.')
    if mode=='copy':shutil.copytree(source,target)
    elif mode=='move':shutil.move(str(source),str(target))
    elif mode=='link':
        try:shutil.copytree(source,target,copy_function=os.link,symlinks=True)
        except OSError:
            if target.exists():shutil.rmtree(target)
            target.symlink_to(source,target_is_directory=True)
    else:raise ValueError('Choose link, copy or move.')
    return str(target)
