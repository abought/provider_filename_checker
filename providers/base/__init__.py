"""Base provider declaring common shared behavior"""
import abc
import typing

import aiohttp


class Provider(abc.ABC):
    BASE_URL = None

    def __init__(self, *args, token: str=None, **kwargs):
        self.token = token
        self.auth_headers = {}

    @abc.abstractmethod
    def authorize(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def upload_file(self, filename, content):
        pass

    # TODO: Add other abstract methods as needed
    # @abc.abstractmethod
    # def create_folder(self, foldername: str):
    #     pass

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

    def authorize(self, *args, token: str=None, **kwargs):
        self.auth_headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-Type': 'application/json'
        }
