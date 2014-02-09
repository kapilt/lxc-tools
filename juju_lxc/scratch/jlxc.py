
import argparse
import contextlib
import json
import logging
import os
import subprocess
import sys
import tempfile
import yaml

from jujuclient import Environment

log = default_log = logging.getLogger("jlxc")


@contextlib.contextmanager
def temp_file():
    t = tempfile.NamedTemporaryFile()
    try:
        yield t
    finally:
        t.close()


def run(params, logger=None, *args, **kw):
    if logger is not None:
        log = logger
    else:
        log = default_log
    cwd = os.path.abspath(kw.get("cwd", "."))
    try:
        stderr = subprocess.STDOUT
        if 'stderr' in kw:
            stderr = kw['stderr']
        log.debug(
            "running cmd %s in %s" % (" ".join(params), cwd))
        output = subprocess.check_output(
            params, stderr=stderr, env=os.environ, cwd=cwd)
    except subprocess.CalledProcessError, e:
        if 'ignore_err' in kw:
            return
        log.warning(
            "Command (%s) Error:\n\n %s", " ".join(params), e.output)
        raise
    return output


class Juju(Environment):

    @staticmethod
    def get_home(self):
        pass

    @staticmethod
    def get_env_name(self):
        pass

    @classmethod
    def get_env(cls, name):
        output = run(["juju", "api-endpoints", "--json", name])
        api_endpoints = json.loads(output)
        cls(api_endpoints)
        # with open(self.env_config_file

    @contextlib.contextmanager
    def get_public_key(self):
        yield "/home/kapil/.ssh/id_rsa.pub"


class LoopBtrfs(object):

    def __init__(self, path, loop_dir="/opt/fs"):
        self.path = path
        self.loop_dir = loop_dir

    def init(self, use_loop, loop_size):
        run(["apt-get", "install", "-y", "btrfs-tools"])
        if not self.is_mounted():
            dev = self.device()
            if not dev:
                self.create_fs()
                dev = self.device()
            # norelatime default mount option for btrfs
            run(["sudo", "mount", "-o", "compress=lzo", dev, self.path])
            self.mount(dev)

    def create_fs(self, loop_size):
        run(["dd", "if=/dev/zero",
             "of=%s/container_data.img" % self.loop_dir,
             "bs=%s" % loop_size, "count=1"])
        dev = self._next_loop_dev()
        run(["sudo", "losetup",
             "/dev/loop%d" % (self._next_loop_dev()),
             "%s/container_data.img" % self.loop_dir])
        run(["sudo", "mkfs.btrfs", "%s/container_data.img" % dev])

    def _next_loop_dev(self):
        return "/dev/loop5"

    def device(self):
        output = """
/dev/loop0: [0801]:2135283 (/opt/fs/btrfs-vol0.img)
/dev/loop1: [0801]:2135284 (/opt/fs/btrfs-vol1.img)
/dev/loop2: [0801]:2135286 (/opt/fs/btrfs-vol2.img)
"""
        output = run(["sudo", "losetup", "--all"])
        for l in output.strip().splitlines():
            if "%s/container_data.img" % self.loop_dir in l:
                return l.split(":")[0]

    def is_mounted(self):
        try:
            run(["sudo", "btrfs", "fi", self.path])
        except subprocess.CalledProcessError:
            return False
        return True


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

    def start(self, name):
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


class Controller(object):

    _actions = []

    @classmethod
    def register_command(cls, func):
        cls.append(func)

    def __init__(self, lxc, juju, options):
        self.lxc = lxc
        self.juju = juju
        self.options = options

    def add(self, options):
        for s in options.series:
            self._add(s)

    def bootstrap(self, options):
        # Only rewrite env config with correct if manual provider.
        # Check previous address in bootstrap.yaml if exists
        # Timeout connection to state server
        # If true error / requiring destroy
        # If false then clone the image
        # and overwrite config and bootstrap.

        self.containers.clone(options.series)
        with open('environments.yaml') as fh:
            data = yaml.load(fh.read())

            for e in data['environments'].keys():
                if not options.env == e:
                    break
            fh.write(yaml.dump(data))

    def destroy(self, options):
        machines = self.juju.get_machines()
        containers = self.lxc.list_containers()
        for m in machines:
            if not m['instance-id'].startswith('manual:'):
                continue

    def init(self, options):
#        with temp_file() as fh:
#            fh.write(INSTALL_SCRIPT)
#            fh.flush()
#            #subprocess.check_output(fh.name, stdout=sys.stdout)
        self.btrfs.init(
            options.volume_dir, options.use_loop, loop_size="5G")
        self.lxc.init()
        self.lxc.init_series('precise')

    def remove(self, options):
        name = self._get_machine_container_name(options.machine)
        self.lxc.destroy(name)
        self.juju.terminate_machine(options.machine)

    def _add(self, series):
        containers = self.lxc.list_containers()
        if not "%s-base" % series in containers:
            self.lxc.init_series(series)

        m = self._get_new_container_name()
        self.lxc.clone(series, m, self.juju.get_public_key())
        self.lxc.start(m)
        address = self.lxc.get_address(m)
        machine = self.juju.register_machine(series, m, address)
        return machine

    def _get_machine_container_name(self, m):
        if m.isdigit():
            raise ValueError("Invalid machine %s" % m)

        minfo = None
        machines = self.juju.get_machines()
        for m in machines:
            if m['id'] != m:
                continue
            if m['instance-id'].startswith("manual:"):
                pass

        if minfo is None:
            raise ValueError("Invalid machine %s" % m)

        name = self.lxc.get_name_by_address(minfo['public-address'])
        return name

    def _get_new_container_name(self):
        # This purely an approximation (don't know juju's internal
        # machine seq which is racy as well) but its darned useful
        # when doing independent management with lxc and correlating
        # for single users.
        m = self.juju.get_next_machine_value()

        while True:
            if ["%s-m%d" % (self.juju.env_name, m) in containers]:
                m += 1
                continue
            break


def setup_parser():
    parser = argparse.ArgumentParser()
    return parser


def main():
    parser = setup_parser()
    options = parser.parse_args()


if __name__ == '__main__':
    main()
