"""A provider that talks to Amazon S3"""
import json
import os
import typing
import urllib.parse

from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat

from ..base import NoAuthProvider
import settings


class S3Provider(NoAuthProvider):
    NAME = 's3'

    S3_ACCESS_KEY = settings.S3_ACCESS_KEY
    S3_SECRET_KEY = settings.S3_SECRET_KEY
    S3_BUCKET = settings.S3_BUCKET

    BASE_URL = None
    BASE_CONTENT_URL = None

    def __init__(self, *args, **kwargs):
        self.connection = S3Connection(self.S3_ACCESS_KEY,
                                       self.S3_SECRET_KEY,
                                       calling_format=OrdinaryCallingFormat())
        self.bucket = self.connection.get_bucket(self.S3_BUCKET, validate=False)

        super(S3Provider, self).__init__(*args, **kwargs)

    async def create_folder(self, foldername: str):
        """
        From WB implementation
        """
        parent_folder = self.parent_folder or ''
        path = os.path.join(parent_folder, foldername)

        url = self.bucket.new_key(path).generate_url(60, 'PUT')

        resp, code = await self._make_request('PUT', url, skip_auto_headers=['CONTENT-TYPE'])
        return resp['id'], code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See 
        """
        #TODO : Implement
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
