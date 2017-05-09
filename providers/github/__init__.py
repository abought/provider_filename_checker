"""A provider that talks to Github"""
import base64
import json
import os
import typing
import urllib.parse

from ..base import OauthBaseProvider
import settings


class GithubProvider(OauthBaseProvider):
    NAME = 'github'

    DEFAULT_CREDENTIAL = settings.GITHUB_AUTH_TOKEN
    BASE_URL = 'https://api.github.com/'
    BASE_CONTENT_URL = None

    # Pseudo folders via gitkeep
    ALLOWS_SUBFOLDERS = True

    async def create_folder(self, foldername: str):
        """
        Create an empty gitkeep file at the specified path
        See: https://developer.github.com/v3/repos/contents/#create-a-file
        """
        # FIXME: This will only work for top level folders (because full path has to be known and in url). Ok for here.
        gk_path = os.path.join(foldername, '.gitkeep')
        data = {
            'content': '',
            'path': gk_path,
            'committer': {
                'name': 'Frodo Baggins',
                'email': 'frodo@sacksville-bagend.org',  # Intentionally fake email; avoid spamming GH activity
            },
            'branch': 'master',  # FIXME: that's right- this is hardcoded
            'message': 'Test of provider filename behaviors'
        }

        path_encoded = urllib.parse.quote(gk_path)
        url = f'{self.BASE_URL}repos/{settings.GH_REPO_NAME}/contents/{path_encoded}'

        resp, code = await self._make_request('PUT', url,
                                              data=json.dumps(data),
                                              headers={'Content-Type': 'application/json'})
        return foldername, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See https://developer.github.com/v3/repos/contents/#create-a-file
        This API is simpler than the `blobs` endpoint used in WB
        """

        # FIXME: This will only work for top level folders (because full path has to be known and in url). Ok for here.
        parent_folder = self.parent_folder or ''
        filename = os.path.join(parent_folder, filename)

        encoded = base64.b64encode(content.encode('utf-8'))
        data = {
            'content': encoded.decode('utf-8'),
            'path': filename,
            'committer': {
                'name': 'Frodo Baggins',
                'email': 'frodo@sacksville-bagend.org',  # Intentionally fake email; avoid spamming GH activity
            },
            'branch': 'master',  # FIXME: that's right- this is hardcoded
            'message': 'Test of provider filename behaviors'
        }

        path_encoded = urllib.parse.quote(filename)
        url = f'{self.BASE_URL}repos/{settings.GH_REPO_NAME}/contents/{path_encoded}'

        return await self.make_request_get_json('PUT', url,
                                                data=json.dumps(data),
                                                headers={'Content-Type': 'application/json'})

    @staticmethod
    def extract_uploaded_filename(payload: dict=None):
        """GH returns the entire path to the entry, not just the filename"""
        return payload['content']['name']
