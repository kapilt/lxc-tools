from jujuclient import Environment as Client


class Juju(object):

    def __init__(self, config):
        self.config = config
        self.client = Client(config.api_url)
        self.client.login(config.api_secret, config.api_user)

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
