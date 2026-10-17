"""Temporary archive preview; the uploaded payload stays packed."""
import os,re,tempfile,shutil
from contextlib import contextmanager
from pathlib import Path
from utils.mediainfo_utils import iter_media_files,is_sample_path
from utils.unrar_upload_utils import find_rar_files,run_mount_command,unmount_path

def preview_error(directory,category,config):
    categories={int(x.strip()) for x in config.get('Settings','RAR2FS_CATEGORIES',fallback='').split(',') if x.strip()}
    screenshots={int(x.strip()) for x in config.get('Settings','SCREENSHOT_CATEGORIES',fallback='').split(',') if x.strip()}
    if not config.getboolean('Settings','SCREENSHOTS',fallback=True) or category not in screenshots:return ''
    if not config.getboolean('Settings','RAR2FS_SCREENSHOTS',fallback=True) or category not in categories:return ''
    if not find_rar_files(directory):return ''
    files=list(iter_media_files(directory))
    if any(not is_sample_path(p) for p in files):return ''
    if files and config.getboolean('Settings','SCREENSHOT_SAMPLE_FALLBACK',fallback=True):return ''
    if os.name!='posix' or not Path('/dev/fuse').exists():return 'RAR screenshots require host FUSE access (/dev/fuse). Start Docker with the UNRAR override, or provide an extracted preview video.'
    binary=config.get('UnrarUpload','RAR2FS_BIN',fallback='rar2fs')
    if not shutil.which(binary) and not (Path(__file__).resolve().parents[1]/'tools/archive/bin/rar2fs').is_file():return 'RAR screenshots require rar2fs. Install archive tools or use the supplied Docker image.'
    return ''

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
    error=preview_error(directory,category,config)
    if error:raise RuntimeError(error)
    if not Path('/dev/fuse').exists() and any(iter_media_files(directory)):
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
