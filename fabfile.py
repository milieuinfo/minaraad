from fabric.api import env, run, cd


def ontwikkel_oud():
    env.hosts = [
        'zope@plone-minaraad-on-1-mgt.mmis.be',
        'zope@plone-minaraad-on-2-mgt.mmis.be',
        ]


def ontwikkel_nieuw():
    env.hosts = [
        'zope@plone-minaraad-on-3-mgt.mmis.be',
        'zope@plone-minaraad-on-4-mgt.mmis.be',
        ]


def oefen_oud():
    env.hosts = [
        'zope@plone-minaraad-oe-1-mgt.mmis.be',
        'zope@plone-minaraad-oe-2-mgt.mmis.be',
        ]


def oefen_nieuw():
    env.hosts = [
        'zope@plone-minaraad-oe-3-mgt.mmis.be',
        'zope@plone-minaraad-oe-4-mgt.mmis.be',
        ]


def productie_oud():
    env.hosts = [
        'zope@plone-minaraad-pr-1-mgt.mmis.be',
        'zope@plone-minaraad-pr-2-mgt.mmis.be',
        ]


def productie_nieuw():
    env.hosts = [
        'zope@plone-minaraad-pr-3-mgt.mmis.be',
        'zope@plone-minaraad-pr-4-mgt.mmis.be',
        ]


def update_ontwikkel():
    """Update Plone on ontwikkel.

    You should run this with 'fab ontwikkel_nieuw update_ontwikkel'.
    """
    with cd('~/buildout'):
        run('bin/supervisorctl shutdown')
        run('git pull')  # TODO
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
