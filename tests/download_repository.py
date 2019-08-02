#!/usr/bin/env python3

import logging
import argparse
import sys
import multiprocessing

import lib


def main():
    parser = argparse.ArgumentParser(
        description="Sync file repositories in parallel",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--processes', type=int, default=1,
                        help='how many parallel processes to use when downloading')
    with lib.status_data(parser) as (args, data):

        for r in data:
            params = []
            pulp_manifest = lib.parse_pulp_manifest(r['remote_url'] + 'PULP_MANIFEST')
            logging.debug("Pulp manifest for %s have %d files" % (r['remote_url'], len(pulp_manifest)))
            for f, _, s in pulp_manifest:
                params.append((r['download_base_url'], f, s))
            logging.debug("Going to use %d processes to download files" % args.processes)
            with multiprocessing.Pool(processes=args.processes) as pool:
                durations = pool.starmap(lib.download, params)
            print("Download times for %s: %s" % (r['remote_url'], lib.data_stats(durations)))

    return 0


if __name__ == '__main__':
    sys.exit(main())
