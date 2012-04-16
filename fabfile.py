from __future__ import with_statement  # For Python2.5 support.
from fabric.api import env, run, cd # local, put
#from fabric.decorators import hosts


def ontwikkel():
    env.hosts = [
        'zope@plone-minaraad-on-1-mgt.mmis.be',
        'zope@plone-minaraad-on-2-mgt.mmis.be',
        ]


def oefen():
    env.hosts = [
        'zope@plone-minaraad-oe-1-mgt.mmis.be',
        'zope@plone-minaraad-oe-2-mgt.mmis.be',
        ]


def productie():
    env.hosts = [
        'zope@plone-minaraad-pr-1-mgt.mmis.be',
        'zope@plone-minaraad-pr-2-mgt.mmis.be',
        ]


def update_ontwikkel():
    """Update Plone on ontwikkel.

    You should run this with 'fab ontwikkel update_ontwikkel'.
    """
    with cd('~/buildout'):
        run('bin/supervisorctl shutdown')
        run('svn up')
        run('bin/buildout')
        run('bin/supervisord')


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
    run('df -h')
