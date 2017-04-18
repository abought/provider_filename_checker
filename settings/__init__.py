try:
    from .local import *
except ImportError:
    print('Must define local settings. Did you remember to copy settings/local-dist.py and update values?')
    raise
