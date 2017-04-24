"""A provider that talks to DropBox"""
import json
import typing
import urllib.parse

from ..base import OauthBaseProvider
import settings

class GoogleDriveProvider(OauthBaseProvider):
    NAME = 'googledrive'

    DEFAULT_CREDENTIAL = settings.GOOGLEDRIVE_OAUTH_TOKEN
    BASE_URL = 'https://www.googleapis.com/drive/v2/'  # TODO: v3 exists but wb uses v2
    BASE_CONTENT_URL = 'https://www.googleapis.com/upload/drive/v2'
    async def create_folder(self, foldername: str):
        """See https://developers.google.com/drive/v3/web/folder"""
        parent_folder = self.parent_folder or 'root'
        url = urllib.parse.urljoin(self.BASE_URL, 'files')
        data = {
            'title': foldername,
            'parents': [
                {'id': parent_folder}
            ],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        resp, code = await self._make_request('POST', url,
                                              data=json.dumps(data),
                                              headers={'Content-Type': 'application/json'})
        return resp['id'], code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See https://developers.google.com/drive/v2/web/simple-upload
        Unlike WB, we will use simple upload method
        """

        #
        parent_folder = self.parent_folder or 'root'
        # Upload files to a different host than the api base url
        url = self.BASE_CONTENT_URL

        size = len(content.encode('utf-8'))
        params = {
            'uploadType': 'media'
        }
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': str(size)
        }

        return await self._make_request('POST', url, data=content, params=params, headers=headers)

    @staticmethod
    def extract_uploaded_filename(payload: dict=None):
        #TODO: Implement
        return payload['name']
