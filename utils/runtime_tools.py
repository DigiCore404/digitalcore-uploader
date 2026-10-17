"""Resolve configured, system or bundled native tools without shell execution."""
import os
import platform
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]


def executable(candidate,name):
    if not candidate.is_file() or not os.access(candidate,os.X_OK):return False
    if name=='mtn' and candidate==ROOT/'bin'/'mtn'/'mtn':
        with candidate.open('rb') as file:prefix=file.read(512)
        if prefix.startswith(b'#!') and b'mtn.bin' in prefix:
            binary=candidate.with_name('mtn.bin')
            return binary.is_file() and os.access(binary,os.X_OK)
    return True


def find_tool(name,config):
    section,key=('Torrent','MKBRR_BIN') if name=='mkbrr' else ('MediaTools','MTNBIN')
    configured=config.get(section,key,fallback='').strip()
    if configured:
        candidate=Path(configured).expanduser()
        if candidate.is_absolute() or '/' in configured or '\\' in configured:
            candidate=candidate if candidate.is_absolute() else ROOT/candidate
            return str(candidate) if executable(candidate,name) else None
        return shutil.which(configured)
    if platform.system()!='Linux':return shutil.which(name)
    machine=platform.machine().lower()
    arch={'amd64':'x86_64','x86_64':'x86_64','aarch64':'arm64','arm64':'arm64','armv7l':'arm','armv6l':'armv6'}.get(machine)
    candidate=ROOT/'bin'/'mkbrr'/'linux'/str(arch)/'mkbrr' if name=='mkbrr' else ROOT/'bin'/'mtn'/'mtn' if arch=='x86_64' else None
    # Prefer our tested versions over an older tool installed by the provider.
    return str(candidate) if candidate and executable(candidate,name) else shutil.which(name)
