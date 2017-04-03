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

from common import make_requests, report


HERE = os.path.dirname(__file__)
SCENARIOS_PATH = os.path.join(os.path.abspath(HERE), 'scenarios')
REPORTS_PATH = os.path.join(HERE, 'reports')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--providers', nargs='*', help='The name of the storage provider(s) to try')
    parser.add_argument('--scenarios', nargs='*', help='The name(s) of the filename trial suite(s) to try')
    parser.add_argument('--delay', default=0.5, type=float,
                        help='The time between requests (throttles to avoid overwhelming server)')
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
            reader = csv.reader(f)
            rows = list(reader)

        for prose, test_fn in rows:
            yield (prose, test_fn)


async def pipeline(provider, scenarios):
    """
    Define a pipeline of tasks to run in series
    :return: 
    """
    # TODO: Rewrite to take better advantage of async behaviors
    # TODO: Take a provider object instead of a string object
    # 1. Authorize for this provider (with credentials)
    # 2. Schedule something on the runloop to start making requests for this provider
    # 3. As responses come in, start writing them to an output file report

    trial_reports = make_requests.serial_requests(provider, scenarios)

    # TODO: need to make sure that we have the provider name when passed a wb provider object
    provider_name = provider  # .NAME
    out_fn = os.path.join(REPORTS_PATH, f'{provider_name}.csv')
    await report.report_writer(trial_reports, provider_name, out_fn=out_fn)


def check_provider(provider_name: str, scenarios: list) -> typing.Awaitable:
    """Import the modules associated with a provider, setup connections, then perform the pipeline of requests"""
    # TODO: Find provider, load associated auth credentials from file, and set up authorization. Then call pipeline
    return asyncio.ensure_future(pipeline(provider_name, scenarios))


def check_providers(*, providers: typing.Iterable[str]=(),
                    scenario_names: typing.List[str]=None) -> typing.List[typing.Awaitable]:
    """Check a series of providers"""
    providers = providers or []
    scenario_filenames = get_scenario_locations(desired_scenarios=scenario_names)
    scenarios = list(load_scenarios(scenario_filenames))
    return [check_provider(provider, scenarios) for provider in providers]


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        raise RuntimeError('For accurate results, must use Python >= 3.6')

    args = parse_args()
    # check_providers(providers=args.providers, scenario_names=args.scenarios)

    loop = loop = asyncio.get_event_loop()
    futures = check_providers(providers=['aprovider', 'bprovider'])
    loop.run_until_complete(asyncio.gather(*futures))
    loop.close()
