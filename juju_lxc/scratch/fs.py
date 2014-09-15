import subprocess
from utils import run


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
