"""
Default configuration for script. Copy to settings/local.py to use.
"""

WB_HOST = 'http://localhost:7777/'
OSF_NODE = None  # Let WB handle credentials/ auth: specify an OSF node that has multiple providers connected

# Non-expiring Personal access tokens/ credentials used to authenticate to various services. Do NOT commit to Github!
WATERBUTLER_OSF_TOKEN = None
DROPBOX_OAUTH_TOKEN = None

# Personal access tokens that expire after x time
BOX_OAUTH_TOKEN = None  # 1 hr, get token from app config page https://app.box.com/developers/services/edit/<app_id>
