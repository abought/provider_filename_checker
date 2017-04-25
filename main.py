"""
Coordinate contacting one or more providers and reporting on the filenames restrictions discovered. Can optionally 
choose to use only a subset of the available filename samples and providers.
"""

import argparse
import asyncio
import csv
import glob
import os
import sys
import typing
import uuid

from common import make_requests, report
import providers


HERE = os.path.dirname(__file__)
SCENARIOS_PATH = os.path.join(os.path.abspath(HERE), 'scenarios')
REPORTS_PATH = os.path.join(HERE, 'reports')

# Intentionally exclude certain WB services: Rackspace cloudfiles, filesystem (used internally only),
# MattF can provide owncloud credentials. For s3 testing, use your own amazon account. For local FigShare, use https,
# or generate a personal token for oauth.
KNOWN_PROVIDERS = {
    'box': providers.BoxProvider,
    'dataverse': providers.WBProvider,
    'dropbox': providers.DropboxProvider,
    'figshare': providers.WBProvider,
    'github': providers.GithubProvider,
    'googledrive': providers.GoogleDriveProvider,
    'osfstorage': providers.WBProvider,
    'owncloud': providers.WBProvider,
    's3': providers.WBProvider
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--providers', nargs='*', default=KNOWN_PROVIDERS.keys(),
                        help='The name of the storage provider(s) to try')
    parser.add_argument('--scenarios', nargs='*', help='The name(s) of the filename trial suite(s) to try')
    parser.add_argument('--wb', action='store_true',
                        help='If flag present, routes all provider requests through Waterbutler API')
    parser.add_argument('--delay', default=0.2, type=float,
                        help='The time between requests, in seconds (throttles to avoid overwhelming server)')
    return parser.parse_args()


def get_scenario_locations(*, desired_scenarios: typing.Iterable = ()) -> list:
    """Get the list of available filename scenarios to test. Optionally filter by name, like `platform-tests`"""
    filenames = glob.glob(os.path.join(SCENARIOS_PATH, '*.csv'))

    if not desired_scenarios:
        return filenames

    # If the user requests only some scenarios, filter the list to be sure they exist
    available = set(os.path.splitext(os.path.basename(fn))[0] for fn in filenames)

    if not set(desired_scenarios).issubset(available):
        raise Exception('Requested unknown scenario(s); exiting.')

    return [os.path.join(SCENARIOS_PATH, name + '.csv') for name in desired_scenarios]


def load_scenarios(filenames: list):
    """Return an iterator over all available test situations"""
    for fn in filenames:
        with open(fn, 'r') as f:
            reader = csv.reader(f, dialect='unix')
            rows = list(reader)

        for prose, test_fn in rows:
            yield (prose, test_fn)


async def pipeline(provider: providers.BaseProvider,
                   scenarios, *,
                   delay: typing.Union[float, None]=None):
    """
    Define a pipeline of tasks to run in series
    
    1. Authorize for this provider (with credentials)
    2. Schedule something on the runloop to start making requests for this provider
    3. As responses come in, start writing them to an output file report
    :return: 
    """
    await provider.authorize()

    # Create a folder where tests will be run
    dest_foldername = uuid.uuid4().hex
    folder_id, code = await provider.create_folder(dest_foldername)
    print('Created folder ', folder_id, ' for provider ', provider.provider_name, code)
    # Some providers can choose to respect this setting for all requests, and do upload tests within this folder
    provider.parent_folder = folder_id

    trial_reports = make_requests.serial_requests(provider, scenarios, delay=delay)

    out_fn = os.path.join(REPORTS_PATH, f'{provider.provider_name}.csv')
    await report.report_writer(trial_reports, provider.provider_name, out_fn=out_fn)


def run_single_provider(provider_name: str,
                        scenarios: list,
                        delay: typing.Union[float, None]=None,
                        use_wb: bool=False) -> typing.Awaitable:
    """Import the modules associated with a provider, setup connections, then perform the pipeline of requests"""
    if use_wb:
        ProviderClass = providers.WBProvider
    else:
        ProviderClass = KNOWN_PROVIDERS[provider_name]

    provider = ProviderClass(provider_name=provider_name)

    return asyncio.ensure_future(pipeline(provider, scenarios, delay=delay))


def main(*, provider_names: typing.Iterable[str]=(),
         scenario_names: typing.List[str]=None,
         delay: typing.Union[float, None]=None,
         use_wb: bool=False) -> typing.List[typing.Awaitable]:
    """Perform filename tests for a series of providers"""
    scenario_filenames = get_scenario_locations(desired_scenarios=scenario_names)
    scenarios = list(load_scenarios(scenario_filenames))
    return [run_single_provider(name, scenarios, delay=delay, use_wb=use_wb) for name in provider_names]


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        raise RuntimeError('For best results, must use Python >= 3.6')

    args = parse_args()

    loop = loop = asyncio.get_event_loop()
    #futures = main(provider_names=args.providers, scenario_names=args.scenarios, delay=args.delay, use_wb=args.wb)
    futures = main(provider_names=['github'], scenario_names=['deleteme'], delay=0.01, use_wb=False)
    loop.run_until_complete(asyncio.gather(*futures))
    loop.close()
