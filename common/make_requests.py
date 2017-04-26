"""
Given a specific provider, handle making a series of requests
"""
import asyncio
import typing

import providers
from . import behaviors
from . import report


async def check_one_filename(provider: providers.BaseProvider,
                             scenario: typing.Tuple[str, str]):
    """Perform a set of upload/download tests for one filename from a list of provided ones"""
    prose, fn = scenario
    print(f'Checking: {provider.provider_name} for {fn}')

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


async def serial_requests(provider: providers.BaseProvider,
                          scenarios: typing.Iterator,
                          delay: typing.Union[float, None]=None) -> typing.AsyncIterator[report.Report]:
    """Make a series of requests to the specified provider"""
    for scenario in scenarios:
        results = await check_one_filename(provider, scenario)
        yield results
        if delay:
            await asyncio.sleep(delay)
