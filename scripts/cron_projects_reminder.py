#!/usr/bin/env python
import sys
import urllib

try:
    import passwords
except ImportError:
    print """
    Add a file named 'passwords.py' in the same directory as this script with
    the following content:

    # Admin username and password to connect to the Zope server:
    USER = 'youradminusername'
    PASS = 'yourpassword'
    # Port that Zope runs on:
    PORT = '8080'
    # id of the Plone Site:
    PLONESITE = 'minaraad'

    For now we'll assume admin/admin, 8080, and minaraad
    """
    passwords = None

if passwords:
    USER = passwords.USER
    PASS = passwords.PASS
    PORT = passwords.PORT
    PLONESITE = passwords.PLONESITE
else:
    USER = 'admin'
    PASS = 'admin'
    PORT = '8080'
    PLONESITE = 'minaraad'


def main(verbose=False):
    if verbose:
        print 'USER: ' + USER
        print 'PASS: ' + PASS
        print 'PORT: ' + PORT
        print 'PLONESITE: ' + PLONESITE

    url = 'http://%s:%s@localhost:%s/%s/@@cron_projects_reminder' % (
        USER, PASS, PORT, PLONESITE)

    if verbose:
        print 'Calling ' + url
    urllib.urlopen(url).read()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(verbose=True)
    else:
        main()
