import logging
import os
import subprocess

log = default_log = logging.getLogger("jlxc")


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
