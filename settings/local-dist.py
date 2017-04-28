"""
Default configuration for script. Copy to settings/local.py to use.
"""

WB_HOST = 'http://localhost:7777/'
OSF_NODE = None  # Let WB handle credentials/ auth: specify an OSF node that has multiple providers connected

# Non-expiring Personal access tokens/ credentials used to authenticate to various services. Do NOT commit to Github!
WATERBUTLER_OSF_TOKEN = None
DROPBOX_OAUTH_TOKEN = None
GITHUB_AUTH_TOKEN = None  # https://github.com/settings/tokens
DATAVERSE_API_TOKEN = None
FIGSHARE_API_TOKEN = None

S3_ACCESS_KEY = None
S3_SECRET_KEY = None

### Personal access tokens that expire after x time
BOX_OAUTH_TOKEN = None  # 1 hr, get token from app config page https://app.box.com/developers/services/edit/<app_id>
GOOGLEDRIVE_OAUTH_TOKEN = None  #  1hr, Get from https://developers.google.com/oauthplayground/ , Scope /auth/drive

# Owncloud apparently doesn't support oauth, which is fun
#  https://doc.owncloud.org/server/latest/developer_manual/core/externalapi.html#authentication-basics
OWNCLOUD_USERNAME = None
OWNCLOUD_APP_PASSWORD = None  # From https://<host>/settings/personal
OWNCLOUD_URL = None

####
#  MISC info required for providers to work
####
# Github provider
GH_REPO_NAME = None  # Of form <username/repo_name> as it appears in github urls. Must have `master` branch!

# S3 Provider
S3_BUCKET = None

# Dataverse: alias id of dataverse we want to connect to (where we will be depositing the data)
DATAVERSE_NAME = None
