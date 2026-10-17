"""Bounded optional notification for new uploader releases."""
import re, requests

def check(version):
    try:
        response=requests.get('https://api.github.com/repos/DigiCore404/digitalcore-uploader/releases/latest',timeout=5,allow_redirects=False)
        if response.status_code!=200:return
        latest=str(response.json().get('tag_name',''))
        def parts(v):return tuple(int(x) for x in re.findall(r'\d+',v)[:3])
        if parts(latest)>parts(version):print('New DigitalCore Uploader release: '+latest+' (https://github.com/DigiCore404/digitalcore-uploader/releases)',flush=True)
    except (requests.RequestException,ValueError,TypeError):pass
