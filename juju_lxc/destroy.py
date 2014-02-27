#!/home/kapil/canonical/jujuclient/bin/python

import argparse
import logging
import os
import subprocess

from utils import connect

log = logging.getLogger('jlxc')


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Remove containers from environment")
    parser.add_argument('-e', "--environment",
                        dest="env_name",
                        default=os.environ.get("JUJU_ENV"),
                        help="Juju environment")
    return parser


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = setup_parser()
    options = parser.parse_args()
    env = connect(options.env_name)

    output = subprocess.check_output(["sudo", "lxc-ls"])
    containers = output.strip().split("\n")

    containers = [c for c in containers
                  if c.startswith('%s-m' % options.env_name)]

    log.info("Destroy containers %s", " ".join(containers))
    for c in containers:
        subprocess.check_output([
            "sudo", "lxc-destroy", "--force", "-n", c])

    m = env.status()
    machines = m['Machines'].keys()
    machines.remove('0')

    log.info("Terminating machines in juju")
    env.destroy_machines(machines, force=True)

if __name__ == '__main__':
    main()
