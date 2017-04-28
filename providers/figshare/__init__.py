"""A provider that talks to Figshare"""
import json
import typing

from ..base import NoAuthProvider
import settings


class FigshareProvider(NoAuthProvider):
    NAME = 'figshare'

    DEFAULT_CREDENTIAL = settings.FIGSHARE_API_TOKEN
    BASE_URL = 'https://api.figshare.com/v2/'
    BASE_CONTENT_URL = None

    async def authorize(self, *args, token: str = None, **kwargs):
        """Set authorization headers, optionally using default credentials if none are explicitly passed"""
        self.token = token or self.DEFAULT_CREDENTIAL
        self.auth_headers = {
            'Authorization': 'token {}'.format(self.token),
        }

    async def create_folder(self, foldername: str):
        """
        Figshare doesn't have folders, but it does have projects + datasets. 
        See https://docs.figshare.com/api/articles/#create-a-new-article
        """
        url = f'{self.BASE_URL}account/articles'
        data = {
            'title': foldername,
            'defined_type': 'fileset'
        }

        resp, code = await self._make_request(
            'POST',
            url,
            data=json.dumps(data)
        )

        article_id = resp['location'].rsplit('/', 1)[1]
        return article_id, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See https://docs.figshare.com/api/file_uploader/#figshare-upload-service
        https://docs.figshare.com/api/upload_example/
        """
        pass
        # parent_folder = self.parent_folder or 'root'
        # # Upload files to a different host than the api base url
        # url = self.BASE_CONTENT_URL
        #
        # size = len(content.encode('utf-8'))
        # params = {
        #     'uploadType': 'multipart'
        # }
        # headers = {
        #     'Content-Type': 'text/plain',
        #     'Content-Length': str(size)
        # }
        #
        # # Construct multipart payload
        # with aiohttp.MultipartWriter('related') as mpwriter:
        #     mpwriter.append_json(
        #         {
        #             'title': filename,
        #             'parents': [{
        #                 'kind': 'drive#parentReference',
        #                 'id': parent_folder
        #             }]
        #         },
        #         headers={'charset': 'UTF-8'}
        #     )
        #     mpwriter.append(content, headers={'Content-Type': 'text/plain'})
        #     return await self._make_request('POST', url, data=mpwriter, params=params, headers=headers)

    @staticmethod
    def extract_uploaded_filename(payload: dict = None):
        # TODO: Implement
        pass
        # return payload['title']
