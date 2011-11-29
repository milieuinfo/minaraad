#!/usr/bin/env python
import sys
import urllib

try:
    import passwords
    passwords  # pyflakes
except ImportError:
    print """
    Add a file named 'passwords.py' in the same directory as this script with
    the following content:

    # Admin username and password to connect to the Zope server:
    USER = 'youradminusername'
    PASS = 'yourpassword'

    # Server name.  This is a new setting that was introduced because
    # the url is used in the e-mails that are sent as well, so on the
    # live site it should NOT be localhost.
    SERVER = 'www.minaraad.be'

    # When SERVER is not localhost or 127.0.0.1, we check the
    # following settings as well, otherwise they are ignored; you
    # should still keep them in the file, just to be on the safe side.
    # An empty string is fine then.

    # Port that Zope runs on:
    PORT = '8080'
    # id of the Plone Site:
    PLONESITE = 'minaraad'

    For now we'll assume admin/admin, localhost, 8080, and minaraad
    """
    passwords = None

# Defaults.
USER = 'admin'
PASS = 'admin'
SERVER = 'localhost'
PORT = '8080'
PLONESITE = 'minaraad'

if passwords:
    # These two are required:
    USER = passwords.USER
    PASS = passwords.PASS
    # The rest is optional (though either SERVER or PORT+PLONESITE
    # should be set).
    try:
        SERVER = passwords.SERVER
    except:
        SERVER = 'localhost'
    try:
        PORT = passwords.PORT
    except:
        pass
    try:
        PLONESITE = passwords.PLONESITE
    except:
        pass

if SERVER not in ('localhost', '127.0.0.1'):
    PORT = ''
    PLONESITE = ''


def main(verbose=False):
    if verbose:
        print 'USER: ' + USER
        print 'PASS: ' + PASS
        print 'SERVER: ' + SERVER
        print 'PORT: ' + PORT
        print 'PLONESITE: ' + PLONESITE

    if PORT and PLONESITE:
        plone_url = '%s:%s/%s' % (SERVER, PORT, PLONESITE)
    else:
        plone_url = SERVER
    url = 'http://%s:%s@%s/@@cron_projects_reminder' % (USER, PASS, plone_url)

    if verbose:
        print 'Calling ' + url
    urllib.urlopen(url).read()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(verbose=True)
    else:
        main()
