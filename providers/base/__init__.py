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

    def __init__(self, *args, provider_name: str=None, **kwargs):
        self.provider_name = provider_name or self.NAME
        self.token = None
        self.auth_headers = {}  # TODO: Move to child class

        # Optionally, run *all* file operations within a specific folder (deliberately not general)
        self.parent_folder = None

    async def _make_request(self,
                            method,
                            url, *,
                            auth=None,
                            data=None,
                            headers: dict=None,
                            params: dict = None,
                            as_json: bool=True) -> typing.Tuple[dict, int]:

        headers = headers or {}
        headers.update(self.auth_headers)  # TODO: Move to child class

        async with aiohttp.request(method, url, auth=auth, data=data, headers=headers, params=params) as resp:
            code = resp.status
            print('Sending request to', url)
            print('Response status:', code, resp.reason)
            print('Response headers: ', resp.headers)
            print('Response body: ', await resp.text())
            json = await resp.json()

        # Most providers provide the key info in resp json. In rare cases we will need the response object instead.
        return json if as_json else resp, code

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
