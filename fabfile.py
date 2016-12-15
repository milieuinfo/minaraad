from fabric.api import env, run, cd, local
import sys
import time


def to_bool(value):
    if isinstance(value, bool):
        return value
    if not isinstance(value, basestring):
        raise ValueError("Must be string: %r" % value)
    if not value:
        return False
    value = value[0].lower()
    # yes/true/ja/1
    if value in ('y', 't', 'j', '1'):
        return True
    # no/false/nee/0
    if value in ('n', 'f', '0'):
        return False
    raise ValueError("Cannot interpret as boolean, try true/false instead: %r"
                     % value)


def ontwikkel():
    env.hosts = [
        'zope@plone-minaraad-on-3-mgt.mmis.be',
        'zope@plone-minaraad-on-4-mgt.mmis.be',
        ]


def oefen():
    env.hosts = [
        'zope@plone-minaraad-oe-3-mgt.mmis.be',
        'zope@plone-minaraad-oe-4-mgt.mmis.be',
        ]


def productie():
    env.hosts = [
        'zope@plone-minaraad-pr-3-mgt.mmis.be',
        'zope@plone-minaraad-pr-4-mgt.mmis.be',
        ]


def release(tag=None, warmup=True):
    """Update Plone.
    """
    warmup = to_bool(warmup)
    if not tag:
        print("ERROR You should run this with e.g. "
              "'fab oefen release:tag=1.2.3' or "
              "'fab ontwikkel release:tag=master'.")
        sys.exit(1)
    with cd('~/buildout'):
        run('bin/supervisorctl shutdown')
        run('git fetch')
        run('git checkout %s' % tag)
        if '.' not in tag:
            # master or other branch
            run('git pull')
        run('bin/buildout')
        run('bin/supervisord')
        if warmup:
            seconds = 10
            print('Sleeping {} seconds before warmup.'.format(seconds))
            time.sleep(seconds)
            run('bin/warmup-all')


def status():
    """Stop Plone.
    """
    with cd('~/buildout'):
        run('git status')
        run('git describe')
        run('bin/supervisorctl status')


def stop():
    """Stop Plone.
    """
    with cd('~/buildout'):
        run('bin/supervisorctl shutdown')


def start():
    """Start Plone.
    """
    with cd('~/buildout'):
        run('bin/supervisord')


def warmup():
    """Warmup Plone/varnish.
    """
    with cd('~/buildout'):
        run('bin/warmup-all')


def info():
    run('w')
    run('free')
    # This lists the NFS blob storage and tells how much disk space it uses.
    # This should be several Gigabytes.
    run('df -h || echo "error during df"')
    status()
