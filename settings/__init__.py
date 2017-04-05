try:
    from .local import *
except ImportError:
    print('Must define local settings. Did you remember to copy settings/local-dist.py and update values?')
    raise

#### Things we should know about waterbutler
# Intentionally exclude: Rackspace cloudfiles, filesystem (used internally only),

# MattF can provide owncloud credentials. For s3 testing, use your own amazon account. For FigShare, use https or
#   personal token for oauth.
KNOWN_PROVIDERS = [
    'box',
    'dataverse',
    'dropbox',
    'figshare',
    'github',
    'googledrive',
    'osfstorage',
    'owncloud',
    's3'
]
