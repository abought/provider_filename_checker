"""Base provider declaring common shared behavior"""
import abc
import typing

import aiohttp


class Provider(abc.ABC):
    BASE_URL = None
    # Default provider name (though we prefer users to pass it in separately)
    NAME = None

    def __init__(self, *args, provider_name: str=None, **kwargs):
        self.provider_name = provider_name or self.NAME
        self.token = None
        self.auth_headers = {}

        # Optionally, run *all* file operations within a specific folder (deliberately not general)
        self.parent_folder = None

    @abc.abstractmethod
    async def authorize(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def upload_file(self, filename, content):
        pass

    @abc.abstractmethod
    def create_folder(self, foldername: str):
        pass

    # TODO: Add other abstract methods as needed
    # @abc.abstractmethod
    # def download_file(self):
    #     pass

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
            json = await resp.json()

        return json, code


class OauthProvider(Provider, abc.ABC):
    def __init__(self, *args, **kwargs):
        super(OauthProvider, self).__init__(*args, **kwargs)

    async def authorize(self, *args, token: str=None, **kwargs):
        self.token = token
        self.auth_headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json'
        }
