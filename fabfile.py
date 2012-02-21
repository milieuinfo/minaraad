from fabric.api import env, run  # local, put, cd
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
    run('cd ~/buildout && bin/supervisorctl shutdown')
    run('cd ~/buildout && svn up')
    run('cd ~/buildout && bin/supervisord')


def stop_plone():
    """Stop Plone.
    """
    run('cd ~/buildout && bin/supervisorctl shutdown')


def info():
    run('w')
    run('free')
    run('df -h')
