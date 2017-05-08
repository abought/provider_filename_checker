"""
Given a specific provider, handle making a series of requests
"""
import asyncio
import typing

import providers
from . import behaviors
from . import report


async def check_one_filename(provider: providers.BaseProvider,
                             scenario: typing.Tuple[str, str]) -> report.Report:
    """Perform a set of upload/download tests for one filename scenario"""
    prose, fn = scenario
    print(f'Checking: {provider.provider_name} for filename {fn}')

    json, code = await provider.upload_file(fn, 'Any text will do')
    their_fn = provider.extract_uploaded_filename(json) if code < 400 else None

    is_match = False
    for match_type, method in behaviors.COMPARISONS.items():
        if their_fn and method(fn, their_fn):
            is_match = match_type
            break

    return report.Report(
        description=prose,
        our_fn=fn,
        their_fn=their_fn,
        upload_status_code=code,
        returned_match=is_match
    )


async def check_one_foldername(provider: providers.BaseProvider,
                               scenario: typing.Tuple[str, str]) -> report.Report:
    """Check whether we can create a folder. We don't verify folder name, so returned_match = None"""
    prose, fn = scenario
    # TODO: Some providers may have a problem with nested folders; check
    print(f'Checking: {provider.provider_name} for foldername {fn}')
    folder_id, code = await provider.create_folder(fn)

    allowed_creation = (code < 400)

    return report.Report(
        description=prose,
        our_fn=fn,
        their_fn=folder_id,
        upload_status_code=code,
        returned_match=None
    )


async def serial_requests(provider: providers.BaseProvider,
                          scenarios: typing.Iterator,
                          delay: typing.Union[float, None]=None) -> typing.AsyncIterator[report.Report]:
    """Make a series of requests to the specified provider"""
    for scenario in scenarios:
        yield await check_one_filename(provider, scenario)
        if delay:
            await asyncio.sleep(delay)

    ####
    # Special scenarios
    if provider.ALLOWS_SUBFOLDERS:
        # Try creating a file and folder with the same name in the same directory.
        folder_then_file = ('Create a folder, then a file with same name (folder)', 'folderthenfile')
        yield await check_one_foldername(provider, folder_then_file)
        if delay:
            await asyncio.sleep(delay)
        folder_then_file = ('Create a folder, then a file with same name (file)', 'folderthenfile')
        yield await check_one_filename(provider, folder_then_file)
        if delay:
            await asyncio.sleep(delay)

        # Same as above, but opposite order (file, then folder)
        file_then_folder = ('Create a file, then a folder with same name (file)', 'filethenfolder')
        yield await check_one_filename(provider, file_then_folder)
        if delay:
            await asyncio.sleep(delay)
        file_then_folder = ('Create a file, then a folder with same name (folder)', 'filethenfolder')
        yield await check_one_foldername(provider, file_then_folder)
