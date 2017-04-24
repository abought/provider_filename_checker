"""A provider that talks to DropBox"""
import json
import typing
import urllib.parse

import aiohttp

from ..base import OauthBaseProvider
import settings

class BoxProvider(OauthBaseProvider):
    NAME = 'box'

    DEFAULT_CREDENTIAL = settings.BOX_OAUTH_TOKEN
    BASE_URL = 'https://api.box.com/2.0/'

    async def create_folder(self, foldername: str):
        """
        See: https://docs.box.com/reference#create-a-new-folder
        """
        # Box is ID based provider. Per docs, root folder id is always 0.
        #   https://docs.box.com/reference#get-folder-info
        parent_folder = self.parent_folder or '0'
        url = urllib.parse.urljoin(self.BASE_URL, 'folders')

        data = {
            'name': foldername,
            'parent': {
                'id': parent_folder
            }
        }
        resp, code = await self._make_request('POST', url,
                                              data=json.dumps(data),
                                              headers={'Content-Type': 'application/json'})
        return resp['id'], code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See: https://docs.box.com/reference#upload-a-file
        """
        # If a parent folder is specified, append it to the URL. Otherwise just add a trailing slash.
        parent_folder = self.parent_folder or '0'
        # Upload files to a different host than the api base url
        url = 'https://upload.box.com/api/2.0/files/content'

        size = len(content.encode('utf-8'))
        # Box uploads are a multipart format
        body = {
            'name': filename,
            'parent': {
                'id': parent_folder
            }
        }

        # Construct multipart upload type
        with aiohttp.MultipartWriter('form-data') as mpwriter:
            mpwriter.append_json(body, {aiohttp.hdrs.CONTENT_DISPOSITION: 'form-data; name="attributes"'})
            mpwriter.append(content, headers={
                aiohttp.hdrs.CONTENT_DISPOSITION: 'form-data; name="file"'
            })

            # TODO: Resume tracing this. Some possible differences involving headers, content length (parts vs whole?)
            for part in mpwriter:
                part.headers.pop(aiohttp.hdrs.CONTENT_LENGTH, None)

            for l in mpwriter.serialize():
                print(l.decode('utf-8'))

            return await self._make_request('POST', url, data=mpwriter)

    @staticmethod
    def extract_uploaded_filename(payload: dict=None):
        # TODO: implement for box
        return payload['name']
