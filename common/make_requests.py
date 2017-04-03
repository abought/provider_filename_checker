"""
Given a specific provider, handle making a series of requests
"""
import asyncio
import typing

from . import behaviors
from . import report

# Handle:
# 1. Authorization
# 2. Throttling
# 3. Taking advantage of asyncio to talk to multiple providers in a more efficient manner

async def check_one_filename(provider, scenario):
    """Perform a set of upload/download tests for one filename from a list of provided ones"""
    prose, fn = scenario

    # TODO: Upload
    # TODO: Download

    # TODO: check a request to format report correctly
    their_fn = 'bob'

    is_match = None
    for match_type, method in behaviors.COMPARISONS.items():
        if method(fn, their_fn):
            is_match = match_type
            break

    return report.Report(
        description=prose,
        our_fn=None,
        their_fn= None,
        upload_status_code= False,
        returned_match= is_match
    )


async def serial_requests(provider, scenarios: typing.Iterator, delay: typing.Union[float, None]=None):  # TODO: python 29198 # -> typing.AsyncGenerator:
    """Make a series of requests to the specified provider"""
    for scenario in scenarios:
        results = await check_one_filename(provider, scenario)
        yield results
        if delay:
            await asyncio.sleep(delay)

