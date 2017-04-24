"""Base provider declaring common shared behavior"""
import abc
import typing

import aiohttp


class BaseProvider(abc.ABC):
    BASE_URL = None
    # Default provider name (though we prefer users to pass it in separately)
    NAME = None

    def __init__(self, *args, provider_name: str=None, **kwargs):
        self.provider_name = provider_name or self.NAME
        self.token = None
        self.auth_headers = {}

        # Optionally, run *all* file operations within a specific folder (deliberately not general)
        self.parent_folder = None

    async def _make_request(self,
                            method,
                            url, *,
                            params: dict=None,
                            headers: dict=None,
                            data=None) -> typing.Tuple[dict, int]:

        headers = headers or {}
        headers.update(self.auth_headers)

        async with aiohttp.request(method, url, params=params, headers=headers, data=data) as resp:
            code = resp.status
            # print('Sending request to', url)
            # print('Response status:', code, resp.reason)
            # print('Response headers: ', resp.headers)
            # print('Response body: ', await resp.text())
            json = await resp.json()

        return json, code

    @abc.abstractmethod
    async def authorize(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def create_folder(self, foldername: str):
        pass

    @abc.abstractmethod
    async def upload_file(self, filename: str, content):
        pass

    @abc.abstractstaticmethod
    def extract_uploaded_filename(payload: dict=None):
        """Given the JSON payload from an upload response, extract the uploaded filename (if possible)"""
        pass


class OauthBaseProvider(BaseProvider, abc.ABC):
    # Allow provider to bake in "default" credentials, eg from a single centralized settings file
    DEFAULT_CREDENTIAL = None

    def __init__(self, *args, **kwargs):
        super(OauthBaseProvider, self).__init__(*args, **kwargs)

    async def authorize(self, *args, token: str=None, **kwargs):
        """Set authorization headers, optionally using default credentials if none are explicitly passed"""
        self.token = token or self.DEFAULT_CREDENTIAL
        self.auth_headers = {
            'Authorization': 'Bearer {}'.format(self.token),
        }
