#!/usr/bin/env python3

import logging
import argparse
import sys

import pulpperf.interact
import pulpperf.structure
import pulpperf.utils
import pulpperf.reporting


def create_repo(name):
    """Create repository"""
    return pulpperf.interact.post('/pulp/api/v3/repositories/',
                                  data={'name': name})['_href']


def create_remote(name, url):
    """Create remote"""
    return pulpperf.interact.post('/pulp/api/v3/remotes/file/file/',
                                  data={'name': name, 'url': url+'PULP_MANIFEST'})['_href']


def start_sync(repo, remote):
    """Start sync of the remote into the repository, return task"""
    return pulpperf.interact.post(remote+'sync/',
                                  data={'repository': repo, 'mirror': False})['task']


def main():
    parser = argparse.ArgumentParser(
        description="Sync file repositories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('repositories', nargs='+',
                        help='file repository(ies) to sync')
    with pulpperf.structure.status_data(parser) as (args, data):

        for r in args.repositories:
            data.append({'remote_url': r})

        for r in data:
            if r['remote_url'] not in args.repositories:
                logging.warning("Skipping creation of %s as it is not in the args" % r['remote_url'])
                continue
            r['repository_name'] = pulpperf.utils.get_random_string()
            r['repository_href'] = create_repo(r['repository_name'])
            logging.debug("Created repository %s" % r['repository_href'])
            r['remote_name'] = pulpperf.utils.get_random_string()
            r['remote_href'] = create_remote(r['remote_name'], r['remote_url'])
            logging.debug("Created remote %s" % r['remote_href'])

        tasks = []
        for r in data:
            if r['remote_url'] not in args.repositories:
                logging.warning("Skipping sync of %s as it is not in the args" % r['remote_url'])
                continue
            task = start_sync(r['repository_href'], r['remote_href'])
            logging.debug("Created sync task %s" % task)
            tasks.append(task)

        results = pulpperf.interact.wait_for_tasks(tasks)
        pulpperf.reporting.report_tasks_stats('Sync tasks', results)

    return 0


if __name__ == '__main__':
    sys.exit(main())
