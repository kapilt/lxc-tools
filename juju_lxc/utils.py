import os
import yaml

from jujuclient import Environment

def _config_from_env(juju_conf):
    data = {}
    with open(juju_conf) as fh:
        cdata = yaml.safe_load(fh.read())
        env_data = cdata.get('bootstrap-config', {})

        if not env_data:
            return

        data['secret'] = env_data.get('admin-secret')
        data['uri'] = "wss://%(bootstrap-host)s:%(api-port)s" % (
            env_data)
        data['bootstrap-host'] = env_data['bootstrap-host']
    return data


def connect(env_name):
    juju_home = os.path.expanduser(os.environ.get("JUJU_HOME", "~/.juju"))
    juju_conf = os.path.join(juju_home, "environments", "%s.jenv" % env_name)
    conf = _config_from_env(juju_conf)
    env = Environment(conf['uri'])
    env.login(conf['secret'])
    return env
