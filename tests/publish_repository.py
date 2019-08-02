#!/usr/bin/env python3

import logging
import argparse
import sys

import lib


def create_publication(repo):
    """Start publication of the repository, return task"""
    return lib.post('/pulp/api/v3/publications/file/file/',
                    data={'repository': repo})['task']


def create_distribution(name, base_path, pub):
    """Start distribution of the repository version, return task"""
    return lib.post('/pulp/api/v3/distributions/file/file/',
                    data={'name': name, 'base_path': base_path, 'publication': pub})['task']


def main():
    parser = argparse.ArgumentParser(
        description="Create publication and distribution on repositories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    with lib.status_data(parser) as (args, data):

        tasks = []
        for r in data:
            task = create_publication(r['repository_href'])
            logging.debug("Created publication task %s" % task)
            tasks.append(task)

        results = lib.wait_for_tasks(tasks)
        print(lib.tasks_table(results))
        print(lib.tasks_min_max_table(results))
        print("Publication tasks waiting time:", lib.tasks_waiting_time(results))
        print("Publication tasks service time:", lib.tasks_service_time(results))

        for i in range(len(results)):
            data[i]['publication_href'] = results[i]['created_resources'][0]

        tasks = []
        for r in data:
            r['distribution_name'] = lib.get_random_string()
            r['distribution_base_path'] = lib.get_random_string()
            task = create_distribution(r['distribution_name'], r['distribution_base_path'], r['publication_href'])
            logging.debug("Created distribution task %s" % task)
            tasks.append(task)

        results = lib.wait_for_tasks(tasks)
        print(lib.tasks_table(results))
        print(lib.tasks_min_max_table(results))
        print("Distribution tasks waiting time:", lib.tasks_waiting_time(results))
        print("Distribution tasks service time:", lib.tasks_service_time(results))

        for i in range(len(results)):
            data[i]['distribution_href'] = results[i]['created_resources'][0]
            data[i]['download_base_url'] = lib.get(data[i]['distribution_href'])['base_url']

    return 0


if __name__ == '__main__':
    sys.exit(main())