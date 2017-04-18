"""
A meta-provider that performs file actions on many different storage hosts, using waterbutler as an intermediary
"""
import urllib.parse

from ..base import OauthProvider
import settings


class WBProvider(OauthProvider):
    BASE_URL = settings.WB_HOST

    def __init__(self, *args, provider=None, **kwargs):
        self.provider = provider
        super(WBProvider, self).__init__(*args, **kwargs)

    async def upload_file(self, filename, content):
        url = urllib.parse.urljoin(self.BASE_URL, f'/v1/resources/{settings.OSF_NODE}/providers/{self.provider}/')
        params = {
            'kind': 'file',
            'name': filename
        }
        resp_json, resp_code = await self._make_request('PUT', url, params=params, data=content)
        print(resp_json, resp_code)
        return resp_json, resp_code
