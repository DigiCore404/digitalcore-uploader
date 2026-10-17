"""Temporary archive preview; the uploaded payload stays packed."""
import os,re,tempfile
from contextlib import contextmanager
from pathlib import Path
from utils.mediainfo_utils import iter_media_files,is_sample_path
from utils.unrar_upload_utils import find_rar_files,run_mount_command,unmount_path

@contextmanager
def media_directory(directory,category,config):
    directory=Path(directory)
    categories={int(x) for x in config.get('Settings','RAR2FS_CATEGORIES',fallback='').split(',') if x.strip()}
    if (not config.getboolean('Settings','RAR2FS_SCREENSHOTS',fallback=True) or category not in categories
            or any(not is_sample_path(p) for p in iter_media_files(directory))):
        yield directory
        return
    archives=[Path(p) for p in find_rar_files(directory) if not is_sample_path(p) and not re.search(r'(?i)\.part(?:[2-9]|[1-9]\d+)\.rar$',p)]
    if not archives:
        yield directory
        return
    parent=Path(config.get('Paths','TMP_DIR'))/str(os.getpid());parent.mkdir(parents=True,exist_ok=True)
    mount=Path(tempfile.mkdtemp(prefix='rar-preview-',dir=parent))
    try:
        run_mount_command(archives[0],mount,parent/'rar-preview.log')
        yield mount
    finally:
        if os.path.ismount(mount) and not unmount_path(mount,parent/'rar-preview.log'):
            raise RuntimeError('Could not unmount temporary RAR preview: '+str(mount))
        # Never recursively remove a FUSE mount or any media it exposes.
        mount.rmdir()
