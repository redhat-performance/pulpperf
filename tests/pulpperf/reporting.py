import datetime
import statistics

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def tasks_table(tasks):
    """Return overview of tasks"""
    out = []
    for t in tasks:
        out.append(t['_href'])
        out.append("    name:\t%s" % t['name'])
        out.append("    created:\t%s" % t['_created'])
        out.append("    started:\t%s" % t['started_at'])
        out.append("    finished:\t%s" % t['finished_at'])
        out.append("    state:\t%s" % t['state'])
    return "\n".join(out)


def tasks_min_max_table(tasks):
    """Return overview of tasks dates min and max in a table"""
    out = "\n%11s\t%27s\t%27s\n" % ('field', 'min', 'max')
    for f in ('_created', 'started_at', 'finished_at'):
        sample = [datetime.datetime.strptime(t[f], DATETIME_FMT)
                  for t in tasks]
        out += "%11s\t%s\t%s\n" \
            % (f,
               min(sample).strftime(DATETIME_FMT),
               max(sample).strftime(DATETIME_FMT))
    return out


def data_stats(data):
    return {
        'samples': len(data),
        'min': min(data),
        'max': max(data),
        'mean': statistics.mean(data),
        'stdev': statistics.stdev(data) if len(data) > 1 else 0.0,
    }


def fmt_data_stats(data):
    # https://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points
    return {
        'samples': data['samples'],
        'min': float('%.02f' % round(data['min'], 2)),
        'max': float('%.02f' % round(data['max'], 2)),
        'mean': float('%.02f' % round(data['mean'], 2)),
        'stdev': float('%.02f' % round(data['stdev'], 2)),
    }


def tasks_waiting_time(tasks):
    """Analyse tasks waiting time (i.e. started_at - _created)"""
    durations = []
    for t in tasks:
        diff = datetime.datetime.strptime(t['started_at'], DATETIME_FMT) \
            - datetime.datetime.strptime(t['_created'], DATETIME_FMT)
        durations.append(diff.total_seconds())
    return fmt_data_stats(data_stats(durations))


def tasks_service_time(tasks):
    """Analyse tasks service time (i.e. finished_at - started_at)"""
    durations = []
    for t in tasks:
        diff = datetime.datetime.strptime(t['finished_at'], DATETIME_FMT) \
            - datetime.datetime.strptime(t['started_at'], DATETIME_FMT)
        durations.append(diff.total_seconds())
    return fmt_data_stats(data_stats(durations))


def fmt_start_end_date(label, start, end):
    return "%s: %s - %s" % (label, start.strftime(DATETIME_FMT), end.strftime(DATETIME_FMT))


def report_tasks_stats(workload, tasks):
    print()
    print(workload)
    print("=" * len(workload))
    print(tasks_table(tasks))
    print(tasks_min_max_table(tasks))
    print("%s waiting time:" % workload, tasks_waiting_time(tasks))
    print("%s service time:" % workload, tasks_service_time(tasks))
