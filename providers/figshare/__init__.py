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

    ALLOWS_SUBFOLDERS = False

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

    async def _initiate_upload(self, parent_dataset, filename, size):
        """First upload step: tell figshare an upload will happen and reserve a place"""
        # First upload placeholder file
        payload = {
            'name': filename,
            'size': str(size)
        }
        placeholder_url = f'{self.BASE_URL}account/articles/{parent_dataset}/files'
        payload, code = await self._make_request('POST', placeholder_url, data=json.dumps(payload))
        return payload, code

    async def _get_file_upload_url(self, article_id, file_id):
        """
        After initiating upload, we need to ask for figshare's upload rules in a separate request
        I have been assured that this is real and not some sort of a weird joke.
        
        Then after we get the upload url, we need to play Figshare may I to be told how to upload
        
        I continue to be told all this is not a weird joke.
        """

        url = f'{self.BASE_URL}account/articles/{article_id}/files/{file_id}'
        payload, code = await self._make_request('GET', url)

        upload_url = payload['upload_url']
        parts_resp_payload, code = await self._make_request('GET', upload_url)
        parts = parts_resp_payload['parts']

        return payload, upload_url, parts

    async def _perform_upload(self, content, upload_url, parts):
        """Second upload step: send data
        This very simple testcase gleefully ignores `parts` information because the chunk we send is so small
        """
        upload_response = None
        code = 400 # If nothing gets uploaded, don't consider this a success
        for part in parts:
            # size = part['endOffset'] - part['startOffset'] + 1  # Ignoring this!
            part_number = part['partNo']
            upload_response, code = await self._make_request(
                'PUT',
                upload_url + '/' + str(part_number),
                data=content,
                # For some reason the file upload endpoints just return the string "ok" instead of a payload
                as_json=False
            )
        # Just return the last response info, or a "failure-esque" placeholder
        return upload_response, code

    async def _mark_upload_complete(self, article_id: str, file_id: str):
        """Last upload step: tell figshare you're done"""
        url = f'{self.BASE_URL}account/articles/{article_id}/files/{file_id}'
        # TODO: This should return a 202 code
        return await self._make_request('POST', url,
                                        # The success response contains XML, not JSON
                                        as_json=False)

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See https://docs.figshare.com/api/file_uploader/#figshare-upload-service
        https://docs.figshare.com/api/upload_example/
        """
        # 1. Initiate (tell figshare to expect a file)
        # 2. Get upload url (and then a list of how figshare wants the file broken up)
        # 3. Upload the content, 1+ requests
        # 4. Make the upload complete
        parent_dataset = self.parent_folder or settings.FIGSHARE_PROJECT
        size = len(content.encode('utf-8'))
        initiate_payload, code = await self._initiate_upload(parent_dataset, filename, size)
        new_file_id = initiate_payload['location'].rsplit('/', 1)[1]

        if code >= 400:
            return {}, code

        metadata_payload, upload_url, parts = await self._get_file_upload_url(parent_dataset, new_file_id)

        # TODO: Upload response?
        upload_resp, code = await self._perform_upload(content, upload_url, parts)

        # We return the code for the last request attempted as final status... but the filename payload is from a
        #   different request, b/c Figshare API is very fragmented. Admittedly this is clunky.
        _, code = await self._mark_upload_complete(parent_dataset, new_file_id)
        return metadata_payload, code

    @staticmethod
    def extract_uploaded_filename(payload: dict = None):
        return payload['name']
