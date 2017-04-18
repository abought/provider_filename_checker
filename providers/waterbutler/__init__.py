"""
A meta-provider that performs file actions on many different storage hosts, using waterbutler as an intermediary
"""
import typing
import urllib.parse

from ..base import OauthProvider
import settings


class WBProvider(OauthProvider):
    BASE_URL = settings.WB_HOST

    # Default name, but prefer users to pass it in explicitly (because this is sort of an indirect provider)
    NAME = 'waterbutler'

    def __init__(self, *args, **kwargs):
        super(WBProvider, self).__init__(*args, **kwargs)

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        url = urllib.parse.urljoin(self.BASE_URL, f'/v1/resources/{settings.OSF_NODE}/providers/{self.provider_name}/')
        params = {
            'kind': 'file',
            'name': filename
        }
        return await self._make_request('PUT', url, params=params, data=content)
