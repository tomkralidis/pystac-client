import argparse
import json
import logging
import os
import sys

from .api import API
from .version import __version__

API_URL = os.getenv('STAC_API_URL', None)


def search(url=API_URL, matched=False, save=None, **kwargs):
    """ Main function for performing a search """

    api = API.open(url)
    search = api.search(**kwargs)

    if matched:
        matched = search.matched()
        print('%s items matched' % matched)
        return

    for item in search.items():
        print(f"{item.id}")

    # print('%s items found' % len(items))

    # print metadata
    # if printmd is not None:
    #     print(items.summary(printmd))

    # print calendar
    # if printcal:
    #     print(items.calendar(printcal))

    # save all metadata in JSON file
    # if save is not None:
    #     items.save(filename=save)


def parse_args(args):
    desc = 'STAC API Client'
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser0 = argparse.ArgumentParser(description=desc)

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument('--version', help='Print version and exit', action='version', version=__version__)
    parent.add_argument('--logging', default='DEBUG', help='DEBUG, INFO, WARN, ERROR, CRITICAL')
    parent.add_argument('--url', help='Root API URL', default=os.getenv('STAC_API_URL', None))
    parent.add_argument('--limit', help='Page size limit', type=int, default=500)
    parent.add_argument('--headers', help='Additional request headers (JSON file or string)', default=None)

    subparsers = parser0.add_subparsers(dest='command')

    # search command
    parser = subparsers.add_parser('search', help='Perform new search of items', parents=[parent], formatter_class=dhf)
    search_group = parser.add_argument_group('search options')

    search_group.add_argument('-c', '--collections', help='One or more collection IDs', nargs='*')
    search_group.add_argument('--ids', help='One or more Item IDs (ignores other parameters)', nargs='*')
    search_group.add_argument('--bbox', help='Bounding box (min lon, min lat, max lon, max lat)', nargs=4)
    search_group.add_argument('--intersects', help='GeoJSON Feature or geometry (file or string)')
    search_group.add_argument('--datetime', help='Single date/time or begin and end date/time '
                                                 '(e.g., 2017-01-01/2017-02-15)')
    # search_group.add_argument('-q', '--query', nargs='*', help='Query properties of form '
    #                                                            'KEY=VALUE (<, >, <=, >=, = supported)')
    search_group.add_argument('--sortby', help='Sort by fields', nargs='*')

    output_group = parser.add_argument_group('output options')
    output_group.add_argument('--matched', help='Print number of matched items and exit',
                              action='store_true', default=False)

    parsed_args = {k: v for k, v in vars(parser0.parse_args(args)).items() if v is not None}

    if 'intersects' in parsed_args:
        if os.path.exists(parsed_args['intersects']):
            with open(parsed_args['intersects']) as f:
                data = json.loads(f.read())
                if data['type'] == 'Feature':
                    parsed_args['intersects'] = data['geometry']
                elif data['type'] == 'FeatureCollection':
                    parsed_args['intersects'] = data['features'][0]['geometry']
                else:
                    parsed_args['intersects'] = data

    return parsed_args


def cli():
    args = parse_args(sys.argv[1:])

    logging.basicConfig(stream=sys.stdout, level=args.pop('logging'))
    # quiet loggers
    for lg in ['urllib3']:
        logging.getLogger(lg).propagate = False

    cmd = args.pop('command')
    if cmd == 'search':
        search(**args)


if __name__ == "__main__":
    cli()
