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
    # TODO: Generate and format report

    # TODO: This is not so useful
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


async def serial_requests(provider, scenarios: typing.Iterator):
    """Make a series of requests to the specified provider"""
    for scenario in scenarios:
        ## TODO: Do this for each fn?
        #
        # TODO: Can this be asyncier?
        results = check_one_filename(provider, scenario)
        yield results
        await asyncio.sleep(0.5)

