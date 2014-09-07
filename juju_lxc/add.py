import argparse
import logging
import os
import subprocess
import tempfile
import uuid

from utils import connect

log = logging.getLogger('jlxc')


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Add container to environment")
    parser.add_argument('-b', "--base", dest="base_name",
                        help="Base container to clone")
    parser.add_argument('-f', "--fs", default="btrfs",
                        choices=("btrfs", "aufs"),
                        help="Filesystem type")
    parser.add_argument('-c', "--count", type=int, default=1,
                        help="Number of containers to create")
    parser.add_argument('-s', "--offset", type=int, default=1,
                        help="Name index offset")

    parser.add_argument('--series', default='precise',
                        help="Series of the container base")
    parser.add_argument('-n', "--nested", action="store_true", default=False,
                        help="Use aa profile to support nested containers")
    parser.add_argument('-e', "--environment",
                        dest="env_name",
                        default=os.environ.get("JUJU_ENV"),
                        help="Juju environment")
    return parser


def add_container(env, container_name, base, fs, series, nested=False):
    log.debug(" Registering container with juju")
    nonce = "manual:%s" % uuid.uuid4().get_hex()
    result = env.register_machine(
        container_name, nonce, series,
        {'Mem': 1024 * 16, 'Arch': 'amd64', 'CpuCores': 2},
        [])

    # Get userdata/juju install script for the machine.
    mid = result['Machine']
    result = env.provisioning_script(mid, nonce, disable_apt=True)

    log.debug(" Cloning container")

    with tempfile.NamedTemporaryFile() as fh:
        fh.write("#!/bin/bash\n")
        fh.write(result['Script'])
        fh.write("\n")
        fh.flush()
        subprocess.check_output(
            ["sudo", "lxc-clone", "-s",
             "-B", fs,
             base, container_name,
             "--", "-u", fh.name, "-i", container_name])

    if nested:
        process = subprocess.Popen(
            ["sudo", "tee", "-a", "/var/lib/lxc/%s/config" % container_name])
        process.stdin.write(
            "lxc.aa_profile = lxc-container-default-with-nesting")
        process.stdin.close()
        process.communicate()

    log.debug(" Starting container as juju machine %s", mid)
    subprocess.check_output(
        ["sudo", "lxc-start", "-d", "-n", container_name])


def main():

    logging.basicConfig(level=logging.DEBUG)
    parser = setup_parser()
    options = parser.parse_args()
    env = connect(options.env_name)

    for i in range(options.offset, options.offset+options.count):
        container_name = "%s-m%d" % (options.env_name, i)
        log.info("Creating container %s", container_name)
        add_container(
            env, container_name, options.base_name, options.fs, options.series)


if __name__ == '__main__':
    main()
