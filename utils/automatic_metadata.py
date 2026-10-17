"""Automatic metadata shared by CLI workers and browser uploads, without replacing explicit choices."""
import re
from pathlib import Path
from utils import tmdb, igdb, tvmaze
from utils.metadata_settings import ignore_words
from utils.release_metadata import extract_metadata

def title_from_release(name, config, kind):
    title=re.sub(r'\.[a-z0-9]{2,4}$','',name,flags=re.I) if Path(name).suffix.lower() in ('.mkv','.mp4','.nsp','.xci','.iso') else name
    title=re.sub(r'-[A-Za-z0-9_]+$','',title)
    title=re.split(r'(?i)[ ._-]+(?:s\d{1,2}(?:e\d{1,3})?|(?:19|20)\d{2})(?:[ ._-]|$)',title,maxsplit=1)[0]
    if kind=='game':title=re.split(r'(?i)[ ._-]+(?:v\d|update|incl|inclu|dlc|multi\d)',title,maxsplit=1)[0]
    title=re.sub(r'[._]+',' ',title)
    for word in sorted(ignore_words(config),key=len,reverse=True):
        phrase=r'[\s._-]+'.join(re.escape(p) for p in re.split(r'[\s._-]+',word) if p)
        title=re.sub(r'(?<!\w)'+phrase+r'(?!\w)',' ',title,flags=re.I)
    return re.sub(r'\s+',' ',title).strip(' -')[:250]

def _ids(config,key):return {int(x.strip()) for x in config.get('Settings',key,fallback='').split(',') if x.strip()}
def _choose(rows,title,year):
    def norm(s):return re.sub(r'\W+','',str(s)).casefold()
    exact=[row for row in rows if norm(row.get('title'))==norm(title)]
    candidates=exact or rows
    if year:
        dated=[row for row in candidates if str(row.get('date','')).startswith(str(year))]
        if dated:return dated[0]
    return candidates[0] if candidates else None

def enrich(directory, category, job, config):
    result=dict(job);explicit=dict(job.get('metadata') or {})
    local=extract_metadata(Path(directory).name,directory=directory)
    local.update({k:v for k,v in explicit.items() if v})
    result['metadata']=local
    kind='game' if category in _ids(config,'GAME_CATEGORIES') else 'tv' if category in _ids(config,'IMDB_TV_CATEGORIES') else 'movie' if category in _ids(config,'IMDB_MOVIE_CATEGORIES') else ''
    if not kind or (kind=='game' and (not config.getboolean('Settings','GAME_INFO',fallback=True) or local.get('gameUrl'))) or (kind!='game' and (not config.getboolean('Settings','IMDB',fallback=True) or local.get('imdbId'))):return result,[]
    title=title_from_release(Path(directory).name,config,kind)
    if len(title)<2:return result,[]
    selected=None
    try:
        print('Looking up '+kind+' metadata: '+title,flush=True)
        if kind=='game':
            cid=config.get('IGDB','CLIENT_ID',fallback='');secret=config.get('IGDB','CLIENT_SECRET',fallback='')
            if not cid or not secret:return result,[]
            selected=_choose(igdb.search(cid,secret,title),title,local.get('release_year'))
            if selected:selected=igdb.detail(cid,secret,selected['id'])
        else:
            token=config.get('TMDB','TOKEN',fallback='') or config.get('TMDB','APIKEY',fallback='')
            if token:
                selected=_choose(tmdb.search(token,title,kind),title,local.get('release_year'))
                if selected:selected=tmdb.detail(token,selected['id'],kind)
            if kind=='tv' and not (selected or {}).get('metadata',{}).get('imdbId'):
                fallback=_choose(tvmaze.search(title),title,local.get('release_year'))
                if fallback:selected=tvmaze.detail(fallback['id'])
    except Exception:
        print('Automatic metadata lookup failed; continuing with NFO and supplied details. Check provider settings.',flush=True)
        return result,[]
    if not selected:return result,[]
    result['_automatic_game'] = kind=='game'
    for key,value in selected.get('metadata',{}).items():
        if value and not result['metadata'].get(key):result['metadata'][key]=value
    if not result.get('description') and selected.get('description'):result['description']=selected['description']
    return result,[] if result.get('images') else selected.get('images',[])

def rehost_images(urls,config):
    from utils.public_download import download
    from utils import image_host
    hosted=[]
    for i,url in enumerate(urls[:4]):
        try:
            raw,_,_=download(url,limit=image_host.MAX_IMAGE)
            hosted.append(image_host.upload(config,'metadata-'+str(i)+'.jpg',raw)['url'])
        except Exception:print('Metadata image could not be rehosted; continuing with local images.',flush=True)
    return hosted
