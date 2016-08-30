from fabric.api import env, run, cd
import sys


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


def update(tag=None):
    """Update Plone.
    """
    if not tag:
        print("ERROR You should run this with e.g. "
              "'fab oefen update:tag=1.2.3' or "
              "'fab ontwikkel update:tag=master'.")
        sys.exit(1)
    with cd('~/buildout'):
        run('bin/supervisorctl shutdown')
        run('git fetch')
        run('git checkout %s' % tag)
        run('bin/buildout')
        run('bin/supervisord')


def status_plone():
    """Stop Plone.
    """
    with cd('~/buildout'):
        run('bin/supervisorctl status')


def stop_plone():
    """Stop Plone.
    """
    with cd('~/buildout'):
        run('bin/supervisorctl shutdown')


def start_plone():
    """Start Plone.
    """
    with cd('~/buildout'):
        run('bin/supervisord')


def info():
    run('w')
    run('free')
    # This lists the NFS blob storage and tells how much disk space it uses.
    # This should be several Gigabytes.
    run('df -h || echo "error during df"')
    status_plone()
