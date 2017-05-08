"""A provider that talks to Owncloud"""
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

    ALLOWS_SUBFOLDERS = True

    @property
    def _webdav_url(self):
        return urllib.parse.urljoin(self.BASE_URL, 'remote.php/webdav/')

    async def _make_request(self, *args, **kwargs):
        return await super(OwncloudProvider, self)._make_request(*args, as_json=False, **kwargs)

    async def create_folder(self, foldername: str):
        """Borrowed heavily from WB implementation"""
        parent_folder = self.parent_folder or ''
        # TODO: Might only work at top level
        url = self._webdav_url + os.path.join(urllib.parse.quote(parent_folder), urllib.parse.quote(foldername))

        resp, code = await self._make_request('MKCOL', url)
        # FIXME: Owncloud response contains an OC-FILEID, but no foldername confirmation. So just assume.
        return foldername, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See https://doc.owncloud.org/server/7.0/user_manual/files/files.html#accessing-files-using-curl
        """
        parent_folder = self.parent_folder or ''
        # TODO: might only work for top-level folders
        url = self._webdav_url + os.path.join(urllib.parse.quote(parent_folder), urllib.parse.quote(filename))
        return await self._make_request('PUT', url, data=content)

    @staticmethod
    def extract_uploaded_filename(payload= None):
        # FIXME: In order to use this feature we will need a future, separate PROPFIND request for metadata; see WB
        pass
        return ''

