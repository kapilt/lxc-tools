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
    parser.add_argument('-c', "--count", type=int, default=1,
                        help="Number of containers to create")
    parser.add_argument('-s', "--offset", type=int, default=1,
                        help="Name index offset")
    parser.add_argument('-e', "--environment",
                        dest="env_name",
                        default=os.environ.get("JUJU_ENV"),
                        help="Juju environment")
    return parser


def add_container(env, container_name, base):
    log.debug(" Registering container with juju")
    nonce = "manual:%s" % uuid.uuid4().get_hex()
    result = env.register_machine(
        container_name, nonce, "precise",
        {'Mem': 1024 * 16, 'Arch': 'amd64', 'CpuCores': 2},
        [])

    # Create userdata for the machine.
    mid = result['Machine']
    result = env.provisioning_script(mid, nonce, disable_apt=True)
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(result['Script'])
    tf.flush()

    log.debug(" Cloning container")
    subprocess.check_output(
        ["sudo", "lxc-clone", "-s", "-B", "btrfs",
         base, container_name,
         "--", "-u", tf.name, "-i", container_name])
    log.debug(" Starting container as juju machine %s", mid)
    with tf:
        subprocess.check_output(
            ["sudo", "lxc-start", "-d", "-n", container_name])


def main():

    logging.basicConfig(level=logging.DEBUG)
    parser = setup_parser()
    options = parser.parse_args()
    env = connect(options.env_name)

    for i in range(options.offset, options.count+1):
        container_name = "%s-m%d" % (options.env_name, i)
        log.info("Creating container %s", container_name)
        add_container(env, container_name, options.base_name)


if __name__ == '__main__':
    main()
