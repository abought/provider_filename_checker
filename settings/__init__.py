try:
    from .local import *
except ImportError:
    print('Must define local settings. Did you remember to copy settings/local-dist.py and update values?')
    raise

# Things we should know about waterbutler
KNOWN_PROVIDERS = [
    'box',
    'cloudfiles',
    'dataverse',
    'dropbox',
    'figshare',
    'filesystem',
    'github',
    'googledrive',
    'osfstorage',
    'owncloud',
    's3'
]
