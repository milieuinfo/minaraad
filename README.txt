===================
Using this buildout
===================

For general comments about using buildout see
http://plone.org/documentation/tutorial/buildout


Note on passwords for cronjobs
------------------------------

Copy scripts/passwords.py.in to scripts/passwords.py and adapt.
This will be used in a cron job.  You may want to hide that file:

$ chmod 600 passwords.py


Getting started
---------------

Get the code, currently from here:

 $ git clone git@bitbucket.org:zestsoftware/minaraad.git
 $ cd minaraad

The first thing you need to do is decide if you are going to use this
buildout for local development, ontwikkel, oefen or productie.  You
should copy the sample buildout.cfg.in file to buildout.cfg::

 $ cp buildout.cfg.in buildout.cfg

Then edit the buildout.cfg file and follow the inline instructions in
that file.  You should at least make sure you extend either devel.cfg,
ontwikkel.cfg, oefen.cfg or productie.cfg and probably set a password
for the database.

Any other .cfg files you see are used by devel/ontwikkel/oefen/productie.cfg
and should not be used directly.

For backgrounds, see this weblog entry and the other documentation it
points to:

http://maurits.vanrees.org/weblog/archive/2008/01/easily-creating-repeatable-buildouts

Now, you need to run:

 $ python2.7 bootstrap.py

This will install the bin/buildout script for you.

To create a Zope instance you now run:

 $ bin/buildout

This will download Plone's eggs and products for you, as well as other
dependencies, create a new Zope 2 installation, and create a new Zope
instance configured with these products.  This will take a while.

You should now start your Zope instance once on the foreground by
running::

 $ bin/instance fg

This should give no errors, and after a while show a message like this::

  INFO Zope Ready to handle requests

Quit it with CTRL-C.  Then start it properly in supervisor (at least
on oefen/productie this is available)::

 $ bin/supervisord


Problem: the site keeps restarting
----------------------------------

If you run ``bin/supervisord`` and the site keeps on restarting, then
there is probably some error that is hard to find with supervisor.  So
shut it down and start the instance on the foreground:

  $ bin/supervisorctl shutdown
  $ bin/instance fg

This will start the site in debug mode and we expect that this will
print an error after a while.  That should give you an idea of what is
actually wrong.  If you do not know what to do with this, copy the
output of the 'bin/instance fg' command and send an email to
support@zestsoftware.nl.


Upgrading an oefen/productie buildout
-------------------------------------

If things go badly wrong a backup is always handy.  We now use
RelStorage in Postgres so backups are not our responsibility anymore.
But we can do something ourselves too if wanted; we can create a
filestorage version in backup.fs::

 $ bin/zodbconvert parts/conf/zodb-relstorage-to-filestorage.cfg

Anyway, now we stop the instance with supervisor::

 $ bin/supervisorctl shutdown

Fetch the code changes from version control::

 $ git fetch

Now switch the buildout to the tag given by Zest, e.g.::

 $ git checkout 6.0.0

Run bin/buildout::

 $ bin/buildout

Watch for any errors.

Start the instance again by starting the supervisor daemon::

 $ bin/supervisord

Watch for any errors in the instance logfile::

 $ tail -f var/log/instance.log

Now you may need to run some upgrade steps or install some products in
the Plone Site control panel.  See the ZEST_RELEASE_NOTES.txt file.
If unsure, ask Zest Software.
