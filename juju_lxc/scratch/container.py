import logging
import os
import subprocess
import sys

from utils import run


log = logging.getLogger('jlxc')


class Lxc(object):

    valid_states = ("active", "frozen", "running", "stopped")
    valid_series = ("precise", "quantal", "raring", "saucy", "trusty")
    cache_dir = "/var/cache/lxc"
    series_img_prefix = "jlxc-"
    series_img_prefix = ""

    def __init__(self, path, key):
        self.path = path
        self.public_key = key
        if self.path:
            assert os.path.exists(self.path) and os.path.isdir(self.path)

    def _series_container(self, series):
        return "%s%s-subvol" % (self.series_img_prefix, series)

    def init(self):
        run(["sudo", "apt-get", "install", "-y",
             "lxc", "cloud-image-tools", "python-yaml"])

    def init_series(self, series):
        assert series in self.valid_series, "Invalid series %s" % series
        containers = self.list_containers()
        if self._series_container(series) in containers:
            return

        # Do some xtra work so we can show image download
        # progress, rather than defer entirely to the templates.

        # TODO normalize to host architecture, as the lxc script
        # defaults to it.
        series_cache_dir = "/var/lib/lxc/cloud-%s" % series
        run(["sudo", "mkdir", "-p", series_cache_dir])
        series_image_url = run(
            ["ubuntu-cloudimg-query", series, "-f", "%{url}"])
        image_name = series_image_url[series_image_url.rfind("/")+1:]
        try:
            run(["sudo", "ls", "%s/%s" % (series_cache_dir, image_name)])
        except subprocess.CalledProcessError, e:
            log.info("Downloading series:%s cloud image", series)
            if e.returncode == 2:
                run(["sudo", "wget", "-v", series_image_url],
                    cwd=series_cache_dir, stdout=sys.stdout)

        params = ["lxc-create", "-B", "btrfs", "-t", "ubuntu-cloud"]
        if self.path:
            params.extend(["-P", self.path])
        params.append(self._series_container(series))
        params.extend(["--", "-r", series, "-S", self.public_key])

        log.info("Creating series %s container", series)
        run(params, stdout=sys.stdout)

    def clone(self, name, series):
        containers = self.list_containers()
        if not self._series_container(series) in containers:
            self.log.info("No series container found, initializing")
            self.init_series(series)
        params = ["sudo", "lxc-clone", "-s", "-B", "btrfs", name]
        params.extend(["--", "-S", self.public_key])
        run(params, stdout=sys.stdout)

    def list_containers(self, state=None, fancy=False):
        params = ["sudo", "lxc-ls"]
        if fancy:
            params.append("--fancy")
        if state:
            assert state in self.valid_states, "Invalid state %s" % state
            params.append("--%s" % state)
        if self.path:
            params.extend(["-P", self.path])
        output = run(params)

        if not fancy:
            return output.strip().splitlines()

        results = []
        lines = iter(output.strip().splitlines())
        headers = lines.next()
        keys = [k.lower() for k in filter(None, headers.split(" "))]

        for l in lines:
            values = [v for v in filter(None, l.split(" "))]
            results.append(dict(zip(keys, values)))
        return results

    def start(self, name, mem=None, cpu=None, volumes=()):
        params = ["sudo", "lxc-start", "-d"]
        if self.path:
            params.extend(["-P", self.path])
        params.extend(["-n", self.name])
        run(params, stdout=sys.stdout)

    def stop(self):
        params = ["sudo", "lxc-stop"]
        if self.path:
            params.extend(["-P", self.path])
        params.extend(["-n", self.name])
        run(params, stdout=sys.stdout)

    def destroy(self, name):
        params = ["sudo", "lxc-destroy", "--force"]
        if self.path:
            params.extend(["-P", self.path])
        params.extend(["-n", self.name])
        run(params, stdout=sys.stdout)
