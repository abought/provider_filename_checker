"""A provider that talks to DropBox"""
import json
import typing
import urllib.parse

from ..base import OauthBaseProvider
import settings

class DropboxProvider(OauthBaseProvider):
    NAME = 'dropbox'

    DEFAULT_CREDENTIAL = settings.DROPBOX_OAUTH_TOKEN
    BASE_URL = 'https://api.dropboxapi.com/2/files/'
    BASE_CONTENT_URL = 'https://content.dropboxapi.com/2/files/'

    ALLOWS_SUBFOLDERS = True

    async def create_folder(self, foldername: str):
        parent_folder = self.parent_folder or '/'
        url = urllib.parse.urljoin(self.BASE_URL, 'create_folder')

        data = {
            'path': f'{parent_folder}{foldername}'
        }
        resp, code = await self._make_request('POST', url,
                                              data=json.dumps(data),
                                              headers={'Content-Type': 'application/json'})
        return resp['path_display'], code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:

        # If a parent folder is specified, append it to the URL. Otherwise just add a trailing slash.
        parent_folder = self.parent_folder or ''
        # Upload files to a different host than the api base url
        url = urllib.parse.urljoin(self.BASE_CONTENT_URL, 'upload')

        size = len(content.encode('utf-8'))
        headers = {
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': json.dumps(
                {'path': f'{parent_folder}/{filename}'}
            ),
            'Content-Length': str(size),
        }
        return await self._make_request('POST', url, headers=headers, data=content)

    @staticmethod
    def extract_uploaded_filename(payload: dict=None):
        return payload['name']
