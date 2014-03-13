import subprocess


class CloudImageRepository(object):

    def search(self, terms):
        series = terms.get('series')
        stream = terms.get('stream')
        print series, stream


    def valid_series(self, series):

        subprocess.check_output(
            "/usr/bin/ubuntu-distro-info")
