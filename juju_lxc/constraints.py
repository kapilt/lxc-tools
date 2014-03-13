import subprocess
import sys


def get_supported_series():
    return subprocess.check_output(
        ["ubuntu-distro-info", "--supported"]).splitlines()


def get_series_image_url(series):
    return subprocess.check_output(
        ['ubuntu-cloudimg-query', series, '-f', '%{url}'])


def download_image(url):
    s = subprocess.Popen(
        ['wget', url], stderr=sys.stderr, stdout=sys.stdout)
    s.communicate()
    s.wait()


def is_btrfs(path):
    mount = get_fs(path)
    return mount['type'] == 'btrfs'


def get_fs(path):
    fs_map = get_fs_map()
    best = None
    for mount in fs_map:
        if path.startswith(mount['path']):
            if (best is None) or len(best['path']) < len(mount['path']):
                best = mount
    return best


def get_fs_map():
    output = subprocess.check_output(["df", "-T"])
    records = []
    for line in output.splitlines()[1:]:
        records.append(
            dict(zip(
                ('dev', 'type', 'blocks', 'used', 'avail', 'use%', 'path'),
                line.split())))
    return records
