"""
For a given provider, generate a report on special characters tested
"""
import csv
import os
import typing


# TODO: Add prose description of each scenario to this report
class Report(typing.NamedTuple):
    description: str
    our_fn: str
    their_fn: str
    upload_status_code: int
    returned_match: typing.Union(str, None)


async def report_writer(reports: typing.AsyncIterator[Report], provider_name: str, *, out_dir=None):
    out_fn = os.path.join(out_dir, f'{provider_name}.csv')

    with open(out_fn, 'r') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        headers = [
            'Scenario name',
            'Filename we sent to server',
            'Filename we got back',
            'Server response code on upload',
            'Filename comparison result'
        ]

        writer.writerow(headers)

        async for r in reports:
            writer.writerow([
                r.description,
                r.our_fn,
                r.their_fn,
                r.upload_status_code,
                r.returned_match
            ])

