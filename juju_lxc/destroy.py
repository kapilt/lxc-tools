#!/home/kapil/canonical/jujuclient/bin/python

import argparse
import logging
import os
import subprocess

from utils import connect

log = logging.getLogger('jlxc')


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Add container to environment")
    parser.add_argument('-c', "--count", type=int, default=1,
                        help="Number of containers to create")
    parser.add_argument('-s', "--offset", type=int, default=1,
                        help="Name index offset")
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

    output = subprocess.check_output(["sudo", "lxc-ls", "--running"])
    containers = output.strip().split("\n")

    containers = [c for c in containers
                  if c.startswith('%s-m' % options.env_name)]

    log.info("Destroy containers %s", " ".join(containers))

    m = env.status()
    machines = m['Machines'].keys()
    machines.remove('0')

    log.info("Terminating machines in juju")
    env.destroy_machines(machines, force=True)


if __name__ == '__main__':
    main()
