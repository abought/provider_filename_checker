"""A provider that talks to Dataverse API 4.5"""
import io
import typing
import xml.sax.saxutils as saxutils
import zipfile

from ..base import NoAuthProvider
import settings


class DataverseProvider(NoAuthProvider):
    # TODO: Uses basic auth, genericize if needed
    NAME = 'dataverse'

    DEFAULT_CREDENTIAL = settings.DATAVERSE_API_TOKEN
    BASE_URL = 'https://demo.dataverse.org/dvn/api/'

    def _dataset_xml(self, datasetname: str) -> str:
        """Generate minimum xml file required to create a new dataset"""
        # TODO: Never do this in production code
        template = """<?xml version="1.0"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:dcterms="http://purl.org/dc/terms/">
   <dcterms:title>{0}</dcterms:title>
   <dcterms:creator>{1}</dcterms:creator>
   <dcterms:subject>{2}</dcterms:subject>
   
   <dcterms:description>{3}</dcterms:description>
   <dcterms:contributor>{4}</dcterms:contributor>
</entry>"""
        title = saxutils.escape(datasetname)

        return template.format(title,
                               'Boughton, Andy',
                               'software',
                               'A sample dataset for filename testing',
                               'samwise.gamgee@sacksville-bagend.net')

    async def _make_request(self, *args, **kwargs):
        return await super(DataverseProvider, self)._make_request(*args, as_json=False, **kwargs)

    async def create_folder(self, foldername: str):
        """
        Dataverse does not appear to have a concept of folders, but dataverses can have datasets.
        http://guides.dataverse.org/en/4.5/api/sword.html#create-a-dataset-with-an-atom-entry
        """
        # TODO: Implement creation of datasets. Requires an XML file with dataset name.
        url = f'{self.BASE_URL}data-deposit/v1.1/swordv2/collection/dataverse/{settings.DATAVERSE_NAME}'
        xml = self._dataset_xml(foldername)

        headers = {
            'Content-type': 'application/atom+xml'
        }
        resp, code = await self._make_request('POST', url, data=xml, headers=headers, auth=(self.DEFAULT_CREDENTIAL,))

        # Dataverse does not return real filename in response
        return foldername, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See http://guides.dataverse.org/en/4.5/api/sword.html#add-files-to-a-dataset-with-a-zip-file
        """
        # TODO: Implement

        stream = io.BytesIO()
        with zipfile.ZipFile(stream) as memzip:
            memzip.writestr(filename, content)

        size = len(stream.getvalue())

        # headers = {'Content-Length': str(len(content.encode('utf-8')))}
        # url = self.bucket.new_key(path).generate_url(60, 'PUT', headers=headers)
        #
        # # FIXME: May need a separate metadata request to get the actual filename
        # return await self._make_request('PUT', url,
        #                                 data=content, headers=headers,
        #                                 skip_auto_headers={'CONTENT-TYPE'}, as_json=False)

    @staticmethod
    def extract_uploaded_filename(payload: dict = None):
        # FIXME: Implement, needing separate metadata request
        pass
        # return payload['title']
