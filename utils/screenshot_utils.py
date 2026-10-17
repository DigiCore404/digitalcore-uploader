"""Screenshot generation using the configured FFmpeg or MTN engine."""
import json
import os
import subprocess
from pathlib import Path
from utils.config_loader import ConfigLoader
from utils.mediainfo_utils import iter_media_files, media_priority, is_sample_path


def generate_screenshots(directory, category_id):
    from utils.rar_preview import media_directory
    config = ConfigLoader().get_config()
    with media_directory(directory, category_id, config) as view:
        files=sorted(iter_media_files(view),key=media_priority)
        main=[p for p in files if not is_sample_path(p)]
        samples=[p for p in files if is_sample_path(p)]
        candidates=main+(samples if config.getboolean('Settings','SCREENSHOT_SAMPLE_FALLBACK',fallback=True) else [])
        if not candidates:
            print('No eligible video found; screenshots skipped.')
            return
        target=Path(config.get('Paths','TMP_DIR'))/str(os.getpid())/'screens'
        target.mkdir(parents=True,exist_ok=True)
        for source in candidates:
            try:return generate_candidate(source,target,config)
            except (OSError,ValueError,KeyError,RuntimeError,subprocess.SubprocessError):
                for image in target.glob('*.jpg'):image.unlink()
                print('Screenshot generation failed for '+source.name+'; trying the next video.',flush=True)
        raise RuntimeError('Screenshots failed for every eligible video.')

def generate_candidate(source,target,config):
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'json', str(source)], capture_output=True, text=True,
                           check=True, timeout=60)
    duration = float(json.loads(probe.stdout)['format']['duration'])
    if duration <= 0:
        raise ValueError('Video duration is not valid.')
    target = Path(config.get('Paths', 'TMP_DIR')) / str(os.getpid()) / 'screens'
    target.mkdir(parents=True, exist_ok=True)
    engine=config.get('MediaTools','SCREENSHOT_ENGINE',fallback='ffmpeg').strip().lower()
    if engine=='mtn':
        from utils.mtn_screenshots import generate
        try:return generate(source,target,duration,config)
        except (OSError,ValueError,RuntimeError,subprocess.SubprocessError):
            if not config.get('MediaTools','MTNBIN',fallback='').strip():raise
            import copy
            fallback=copy.deepcopy(config);fallback.set('MediaTools','MTNBIN','')
            for image in target.glob('*.jpg'):image.unlink()
            print('Configured MTN failed; trying the bundled/system MTN.',flush=True)
            return generate(source,target,duration,fallback)
    if engine!='ffmpeg':raise ValueError('Choose ffmpeg or mtn as the screenshot engine.')
    count = min(12, max(1, config.getint('MediaTools', 'SCREENSHOT_SINGLES', fallback=5)))
    for i in range(1, count + 1):
        output = target / f'screenshot-{i:02d}.jpg'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                        '-ss', str(duration * i / (count + 1)), '-i', str(source),
                        '-frames:v', '1', '-vf', 'scale=min(1280\\,iw):-2',
                        '-q:v', '3', str(output)], check=True, timeout=90)
        if not output.exists() or not output.stat().st_size:
            raise RuntimeError(f'Screenshot {i} could not be generated.')
        print(f'Screenshots: {i}/{count}', flush=True)
