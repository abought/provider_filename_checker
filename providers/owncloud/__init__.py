"""A provider that talks to Owncloud"""
import json
import os
import typing
import urllib.parse

from ..base import BasicAuthProvider
import settings


class OwncloudProvider(BasicAuthProvider):
    NAME = 'owncloud'

    USERNAME = settings.OWNCLOUD_USERNAME
    PASSWORD = settings.OWNCLOUD_APP_PASSWORD

    BASE_URL = settings.OWNCLOUD_URL
    BASE_CONTENT_URL = None

    @property
    def _webdav_url(self):
        return urllib.parse.urljoin(self.BASE_URL, 'remote.php/webdav/')

    async def _make_request(self, *args, auth=None, **kwargs):
        return await super(OwncloudProvider, self)._make_request(*args, as_json=False, **kwargs)

    async def create_folder(self, foldername: str):
        """Borrowed heavily from WB implementation"""
        parent_folder = self.parent_folder or ''
        # TODO: Might only work at top level
        url = self._webdav_url + os.path.join(parent_folder, foldername)

        resp, code = await self._make_request('MKCOL', url)

        info = {'name': foldername, 'OC-FILEID': resp.headers.get('OC-FILEID')}
        return info, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See https://developers.google.com/drive/v2/web/multipart-upload
        (use multipart for simple, non-resumable uploads with metadata)
        """
        # parent_folder = self.parent_folder or 'root'
        # # Upload files to a different host than the api base url
        # url = self.BASE_CONTENT_URL
        #
        # size = len(content.encode('utf-8'))
        # params = {
        #     'uploadType': 'multipart'
        # }
        # headers = {
        #     'Content-Type': 'text/plain',
        #     'Content-Length': str(size)
        # }
        #
        # # Construct multipart payload
        # with aiohttp.MultipartWriter('related') as mpwriter:
        #     mpwriter.append_json(
        #         {
        #             'title': filename,
        #             'parents': [{
        #                 'kind': 'drive#parentReference',
        #                 'id': parent_folder
        #             }]
        #         },
        #         headers={'charset': 'UTF-8'}
        #     )
        #     mpwriter.append(content, headers={'Content-Type': 'text/plain'})
        #     return await self._make_request('POST', url, data=mpwriter, params=params, headers=headers)

    @staticmethod
    def extract_uploaded_filename(payload: dict = None):
        pass
        # TODO: Implement
        # return payload['title']
