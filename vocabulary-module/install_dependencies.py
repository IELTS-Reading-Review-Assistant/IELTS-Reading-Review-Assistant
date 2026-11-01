"""Normalise Windows system proxy URLs for pip without changing system settings."""
import os
import subprocess
import sys
import urllib.request
from urllib.parse import urlsplit, urlunsplit

env = os.environ.copy()
proxy = urllib.request.getproxies().get('https')
if proxy:
    parsed = urlsplit(proxy if '://' in proxy else 'http://' + proxy)
    if parsed.hostname in ('localhost', '127.0.0.1', '::1'):
        proxy = urlunsplit(('http', parsed.netloc, parsed.path, parsed.query, parsed.fragment))
    env['HTTPS_PROXY'] = proxy
    env['HTTP_PROXY'] = proxy
sys.exit(subprocess.call([sys.executable, '-m', 'pip', 'install', '-r',
                          'requirements.txt'], env=env))
