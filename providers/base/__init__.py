"""Base provider declaring common shared behavior"""
import abc
import typing

import aiohttp


class BaseProvider(abc.ABC):
    # Base url for api requests
    BASE_URL = None
    # Some providers define a different URL for file uploads
    BASE_CONTENT_URL = None

    # Default provider name (though we prefer users to pass it in separately)
    NAME = None

    # Whether the provider allows subfolders below the top level. Some, like Figshare, organize things differently.
    ALLOWS_SUBFOLDERS: bool = True

    def __init__(self, *args, provider_name: str=None, **kwargs):
        self.provider_name: str = provider_name or self.NAME
        self.token: str = None
        self.auth_headers: dict = {}  # TODO: Move to child class

        # Optionally, run *all* file operations within a specific folder (deliberately not general)
        self.parent_folder: str = None

    async def _make_request(self,
                            method,
                            url, *,
                            auth=None,
                            data=None,
                            headers: dict=None,
                            params: dict = None,
                            **kwargs) -> typing.Tuple[aiohttp.client.ClientResponse, int]:

        headers = headers or {}
        headers.update(self.auth_headers)  # TODO: Move to child class

        async with aiohttp.request(method, url, auth=auth, data=data, headers=headers, params=params, **kwargs) as resp:
            code = resp.status

            print('Sending request to', url, '\n')
            print('Response status:', code, resp.reason, '\n')
            print('Response headers: ', resp.headers, '\n')
            print('Response body: ', await resp.text(), '\n\n\n')

        return resp, code

    async def make_request_get_json(self, *args, **kwargs) \
            -> typing.Tuple[typing.Union[aiohttp.client.ClientResponse, dict], int]:
        """
        Many clients will want to parse the response payload as JSON. We will only do this on success for now due to 
        edge cases in some providers. (eg dropbox returns JSON for success, but text or HTML for some error types)
        """
        resp, code = await self._make_request(*args, **kwargs)
        if code < 400:
            return await resp.json(), code
        else:
            return resp, code

    @abc.abstractmethod
    async def authorize(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    async def create_folder(self, foldername: str) -> typing.Tuple[str, int]:
        pass

    @abc.abstractmethod
    async def upload_file(self, filename: str, content) \
            -> typing.Tuple[typing.Union[dict, aiohttp.client.ClientResponse], int]:
        pass

    @abc.abstractstaticmethod
    def extract_uploaded_filename(payload: dict=None):
        """Given the JSON payload from an upload response, extract the uploaded filename (if possible)"""
        pass


class NoAuthProvider(BaseProvider, abc.ABC):
    """Provider that does not perform any global authorization (implementation must handle on each request)"""
    async def authorize(self, *args, **kwargs):
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


class BasicAuthProvider(BaseProvider, abc.ABC):
    """
    Authenticate via HTTP Basic Auth
    """
    USERNAME = None
    PASSWORD = None

    def __init__(self, *args, **kwargs):
        super(BasicAuthProvider, self).__init__(*args, **kwargs)
        self._auth = None

    async def authorize(self, *args, username: str=None, password: str=None, **kwargs):
        username = username or self.USERNAME
        password = password or self.PASSWORD
        self._auth = aiohttp.BasicAuth(username, password)

    async def _make_request(self, *args, auth=None, **kwargs):
        return await super(BasicAuthProvider, self)._make_request(*args, auth=self._auth, **kwargs)
