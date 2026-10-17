"""Choose a working screenshot engine for a fresh native installation."""
import configparser
from pathlib import Path
from utils.runtime_tools import find_tool
ROOT=Path(__file__).resolve().parents[1]

def configure(path,new=False):
    path=Path(path);config=configparser.ConfigParser(interpolation=None);config.read([ROOT/'defaults.ini',path])
    engine=config.get('MediaTools','SCREENSHOT_ENGINE',fallback='mtn')
    if not config.getboolean('Settings','SCREENSHOTS',fallback=True) or engine!='mtn' or find_tool('mtn',config):return engine
    if not new:raise ValueError('MTN is not installed. Existing settings were preserved. Install MTN or select MediaTools.SCREENSHOT_ENGINE = ffmpeg.')
    saved=configparser.ConfigParser(interpolation=None);saved.read(path)
    if not saved.has_section('MediaTools'):saved.add_section('MediaTools')
    saved.set('MediaTools','SCREENSHOT_ENGINE','ffmpeg')
    with path.open('w',encoding='utf-8') as file:saved.write(file)
    path.chmod(0o600)
    print('MTN is not bundled in this checkout; the new native configuration uses FFmpeg screenshots.')
    return 'ffmpeg'
