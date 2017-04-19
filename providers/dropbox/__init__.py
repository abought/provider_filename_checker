from ..base import OauthBaseProvider
import settings

class DropboxProvider(OauthBaseProvider):
    NAME = 'dropbox'

    DEFAULT_CREDENTIAL = settings.DROPBOX_OAUTH_TOKEN
    BASE_URL = 'https://api.dropboxapi.com/2'
