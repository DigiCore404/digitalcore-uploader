"""Create a local self-signed certificate as the ordinary seedbox user."""
import re,shutil,subprocess,sys
from pathlib import Path

def create(host,root=None):
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?',host):raise ValueError('Use a hostname without a URL or port.')
    root=Path(root) if root else Path(__file__).resolve().parents[1]
    folder=root/'certificates';folder.mkdir(mode=0o700,exist_ok=True)
    cert=folder/'cert.pem';key=folder/'key.pem'
    if cert.exists() or key.exists():
        if not cert.is_file() or not key.is_file():raise ValueError('Incomplete certificate pair; existing files were preserved.')
        return cert,key
    if not shutil.which('openssl'):raise ValueError('OpenSSL is required for --https. Ask your provider to install it.')
    subprocess.run(['openssl','req','-x509','-newkey','ec','-pkeyopt','ec_paramgen_curve:secp384r1','-nodes','-days','3650','-keyout',str(key),'-out',str(cert),'-subj','/CN='+host,'-addext','subjectAltName=DNS:'+host],check=True,capture_output=True)
    key.chmod(0o600);cert.chmod(0o644)
    return cert,key
if __name__=='__main__':
    create(sys.argv[1] if len(sys.argv)>1 else 'localhost')
    print('HTTPS certificate ready; existing certificates are preserved.')
