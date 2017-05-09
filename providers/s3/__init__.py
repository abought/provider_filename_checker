"""A provider that talks to Amazon S3"""
import os
import typing

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

    # Pseudo/ abstraction layer. See http://docs.aws.amazon.com/AmazonS3/latest/UG/FolderOperations.html
    #  "The Amazon S3 console treats all objects that have a forward slash "/" character as the last (trailing)
    #   character in the key name as a folder, for example examplekeyname/."
    ALLOWS_SUBFOLDERS = True

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
        # TODO: May need separate metadata fetch for file content info??
        return foldername, code

    async def upload_file(self, filename: str, content):
        """
        See 
        """
        # TODO: May only work for top level folders
        parent_folder = self.parent_folder or ''
        # TODO/ FIXME: This gets appended to the URL and  might need to be encoded?
        path = os.path.join(parent_folder, filename)

        # TODO: Don't encrypt uploads for now, but this may change
        headers = {'Content-Length': str(len(content.encode('utf-8')))}
        url = self.bucket.new_key(path).generate_url(60, 'PUT', headers=headers)

        # FIXME: May need a separate metadata request to get the actual filename
        return await self._make_request('PUT', url,
                                        data=content, headers=headers,
                                        skip_auto_headers={'CONTENT-TYPE'})

    @staticmethod
    def extract_uploaded_filename(payload: dict = None):
        # FIXME: Implement, needing separate metadata request
        pass
        # return payload['title']
