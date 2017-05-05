Upgrade Minaraad to Ubuntu 1404
===============================

Start situation: Ubuntu 10.10 on ontwikkel-1 and ontwikkel-2.

Wanted situation: Ubuntu 14.04 LTS on ontwikkel-3 and ontwikkel-4.

Same for oefen and productie servers.

The rest of the setup basically stays the same:

- Python 2.7

- Plone 4.2.7

- Database in RelStorage

- Blob files on NFS, mounted at the minaraad-blobs directory.

What follows is a list of steps taken by Maurits at both ontwikkel
servers. This should be done on the oefen and production servers too.


Ubuntu version
--------------

Check that the server indeed has Ubuntu 14.04.something LTS::

    cat /etc/issue


Blobs
-----

Check that the blobs are mounted via NFS on
``/home/zope/minaraad-blobs``.  The zope user must be able to read and
write this location::

    cat /etc/fstab
    cat minaraad-blobs/.layout  # must be 'bushy' without a line ending
    ls -laR minaraad-blobs/
    touch minaraad-blobs/foo && rm minaraad-blobs/foo


Extra packages
--------------

::

    sudo apt-get install build-essential emacs23-nox gcc patch subversion \
    git-core poppler-utils wv python2.7-dev libjpeg8-dev munin-node \
    libreadline-dev libexpat1-dev zlib1g-dev libssl-dev libxml2-dev \
    libxslt1-dev python-virtualenv libldap2-dev libsasl2-dev \
    libsqlite3-dev postgresql-client libpq-dev


Proxy
-----

We need to access the outside world via a proxy.  apt-get has its
own config for this, so it already works.  But we need to fetch
subversion info and Python packages too, and the minaraad site needs
to access a recaptcha service, so we need to setup a proxy.

If both of these commands work, you can skip this step::

    wget https://google.be
    svn ls https://svn.milieuinfo.be/productie/svn/websites/minaraad/trunk

Both are expected to give an error like 'Unable to connect'.

You could use an old script to fix this still, but the last version
requires you to still manually edit /etc/bash/bashrc, so let's not
use it.  For reference though, here it is:

https://svn.milieuinfo.be/productie/svn/websites/plone/install_scripts/trunk/setup_environment.sh

Add this to /etc/bash.bashrc:

    # MMIS Proxy settings for HTTP and HTTPS
    export HTTP_PROXY=http://forward-proxy-76.mmis.be:3128
    export HTTPS_PROXY=http://forward-proxy-76.mmis.be:3128
    export http_proxy=http://forward-proxy-76.mmis.be:3128
    export https_proxy=http://forward-proxy-76.mmis.be:3128

The number (76) differs on ontwikkel/oefen/productie.  If `ifconfig`
says your IP is 192.168.76.28 the number will be 76.

Note: you might want to search for bash completion in that file and
enable it.  I always like this.

You must exit the shell and open a fresh ssh connection for this to
take effect.  Check that the proxy works::

    wget https://google.be

Call subversion once, to create a ~/.subversion directory with settings::

    svn --version

Add this to the end of the ~/.subversion/servers file::

    # MMIS Proxy settings for HTTP and HTTPS
    http-proxy-host=forward-proxy-76.mmis.be
    http-proxy-port=3128


In that same file, you may to switch off storing plaintext
passwords.  Or switch it on explicitly.

::

    store-plaintext-passwords = no


Buildout
--------

Make a checkout in the /home/zope/buildout directory::

    svn co https://svn.milieuinfo.be/productie/svn/websites/minaraad/trunk buildout
    cd buildout

Copy the ``buildout.cfg.in`` template and edit the ``buildout.cfg`` file for
this machine.  You must at least choose a base config and set a
password for the Postgres database.  And maybe enable some parts.
The inline documentation in this file should help you.

::

    cp buildout.cfg.in buildout.cfg

Now run the buildout.  This will take a while::

    python2.7 bootstrap.py
    bin/buildout

Start the instance once on the foreground to see if it starts up well::

    bin/instance fg

When all is well, stop it with CTRL_C and start it properly::

    bin/supervisord
