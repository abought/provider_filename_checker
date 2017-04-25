"""A provider that talks to Github"""
import functools
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
            'branch': 'master',  # FIXME: ayup, this is hardcoded
            'message': 'Test of provider filename behaviors'
        }

        # TODO: should foldername be in url, or is payload sufficient?
        path_encoded = urllib.parse.quote(gk_path)
        url = f'{self.BASE_URL}repos/{settings.GH_REPO_NAME}/contents/{path_encoded}'

        resp, code = await self._make_request('PUT', url,
                                              data=json.dumps(data),
                                              headers={'Content-Type': 'application/json'})
        return foldername, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        # TODO: Implement

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
        """GH returns the entire path to the entry, not just the filename"""
        path = payload['path']
        return os.path.basename(path)
