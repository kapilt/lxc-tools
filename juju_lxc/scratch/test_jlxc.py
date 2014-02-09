import unittest2
import mock

import jlxc


class TestLxc(unittest2.TestCase):

    def setUp(self):
        self.lxc_path = "/var/lib/lxc"
        self.key_path = "/tmp/id_dsa.pub"
        self.lxc = jlxc.Lxc(self.lxc_path, self.key_path)

    def tearDown(self):
        pass

    @mock.patch('jlxc.run')
    def test_list_containers(self, run):
        self.lxc.init()
        run.assert_called_with(
            ['sudo', 'apt-get', 'install', '-y', 'lxc',
             'cloud-image-tools', 'python-yaml'])

    def test_init_series(self):
        pass

    def test_clone(self):
        pass

    def test_start(self):
        pass

    def test_stop(self):
        pass


class TestController(unittest2.TestCase):

    def test_add(self):
        pass

    def test_add_no_series(self):
        pass

    def test_bootstrap(self):
        pass

    def test_remove(self):
        pass

    def test_destroy(self):
        pass


if __name__ == '__main__':
    unittest2.main()
