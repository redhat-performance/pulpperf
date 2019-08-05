import requests
import tempfile
import time

from .utils import measureit, urljoin

BASE_ADDR = "http://localhost:24817"
CONTENT_ADDR = "http://localhost:24816"


def get(url, params={}):
    """Wrapper around requests.get with some simplification in our case"""
    url = BASE_ADDR + url

    r = requests.get(url=url, params=params)
    r.raise_for_status()
    data = r.json()
    return data


def get_results(url, params={}):
    """Wrapper around requests.get with some simplification in our case"""
    out = []
    page = 0
    while True:
        data = get(url, params)
        out += data['results']
        page += 1
        params['page'] = page
        if data['next'] is None:
            break
    return out


def post(url, data):
    """Wrapper around requests.post with some simplification in our case"""
    url = BASE_ADDR + url

    r = requests.post(url=url, json=data)
    r.raise_for_status()
    return r.json()


def download(base_url, file_name, file_size):
    """Downlad file with expected size and drop it"""
    with tempfile.TemporaryFile() as downloaded_file:
        full_url = urljoin(CONTENT_ADDR, base_url, file_name)
        duration, response = measureit(requests.get, full_url)
        response.raise_for_status()
        downloaded_file.write(response.content)
        assert downloaded_file.tell() == file_size
        return duration


def wait_for_tasks(tasks):
    """Wait for tasks to finish, returning task info. If we time out,
    list of None is returned."""
    start = time.time()
    out = []
    timeout = 7200
    step = 3
    for t in tasks:
        while True:
            now = time.time()
            if now >= start + timeout:
                out.append(None)
                break
            response = get(t)
            if response['state'] in ('failed', 'cancelled', 'completed'):
                out.append(response)
                break
            else:
                time.sleep(step)
    return out
