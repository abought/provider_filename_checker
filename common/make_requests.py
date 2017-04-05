"""
Given a specific provider, handle making a series of requests
"""
import asyncio
import typing
import urllib.parse

import aiohttp

from . import behaviors
from . import report
import settings

# Handle:
# 1. Authorization
# 2. Throttling
# 3. Taking advantage of asyncio to talk to multiple providers in a more efficient manner


async def check_one_filename(provider: str,
                             scenario: typing.Tuple[str, str]):
    """Perform a set of upload/download tests for one filename from a list of provided ones"""
    prose, fn = scenario
    print(f'Checking: {provider} for {fn}')

    params = {
        'kind': 'file',
        'name': fn
    }
    headers = {'Authorization': f'Bearer {settings.OSF_TOKEN}'}
    url = urllib.parse.urljoin(settings.WB_HOST, f'/v1/resources/{settings.OSF_NODE}/providers/{provider}/')

    async with aiohttp.put(url, params=params, headers=headers, data='Any text will do') as resp:
        code = resp.status
        json = await resp.json()
        their_fn = json['data']['attributes']['name'] if code < 400 else None

    is_match = None
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


async def serial_requests(provider: str,
                          scenarios: typing.Iterator,
                          delay: typing.Union[float, None]=None):  # TODO: python bug 29198 # -> typing.AsyncGenerator:
    """Make a series of requests to the specified provider"""
    for scenario in scenarios:
        results = await check_one_filename(provider, scenario)
        yield results
        if delay:
            await asyncio.sleep(delay)
