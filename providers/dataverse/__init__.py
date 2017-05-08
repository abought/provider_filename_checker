"""A provider that talks to Dataverse API 4.5"""
import io
import re
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

    ALLOWS_SUBFOLDERS = False

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

        # For uploading, we need the DOI of the resource, because THIS IS SPARTA
        # Well. The XML format only gives links, so, we're not getting this out without a regex anyway
        if code < 400:
            match = re.search('(10.[a-zA-Z0-9\/]+)', await resp.text())
            # Future dataset operations require the DOI (not the title or alias etc)
            return match.group(), code
        else:
            return None, code

    async def upload_file(self,
                          filename: str,
                          content) -> typing.Tuple[dict, int]:
        """
        See http://guides.dataverse.org/en/4.5/api/sword.html#add-files-to-a-dataset-with-a-zip-file
        
        This script is focused on uploading files one at a time. In production use, zipfile upload could be handled 
        more efficiently as a bulk request.
        """
        doi = self.parent_folder  # Every file we upload needs a dataset specified in advance!

        stream = io.BytesIO()

        with zipfile.ZipFile(stream, mode='w', compression=zipfile.ZIP_DEFLATED) as memzip:
            memzip.writestr(filename, content)

        url = f'{self.BASE_URL}data-deposit/v1.1/swordv2/edit-media/study/doi:{doi}'
        size = len(stream.getvalue())
        stream.seek(0, 0)

        headers = {
            "Content-Disposition": "filename=temp.zip",
            "Content-Type": "application/zip",
            "Packaging": "http://purl.org/net/sword/package/SimpleZip",
            "Content-Length": str(size),
        }

        return await self._make_request('POST', url, auth=(self.DEFAULT_CREDENTIAL,),
                                        data=stream, headers=headers)

    @staticmethod
    def extract_uploaded_filename(payload: dict = None):
        # FIXME: Implement, needing separate metadata request
        pass
        # return payload['title']
