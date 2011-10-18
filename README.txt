===================
Using this buildout
===================

For general comments about using buildout see the file
``buildout.txt`` and http://plone.org/documentation/tutorial/buildout


Note on cronjob for production
------------------------------

Copy scripts/passwords.py.in to scripts/passwords.py and adapt.
This will be used in a cron job.  You may want to hide that file:

$ chmod 600 passwords.py


Getting started
---------------

The first thing you need to do is decide if you are going to use this
buildout for development, preview or production.  You need to create a
symbolic link from buildout.cfg to the correct .cfg file.

For development:

 $ ln -s devel.cfg buildout.cfg

For preview:

 $ ln -s preview.cfg buildout.cfg

For production:

 $ ln -s production.cfg buildout.cfg

Any other .cfg files you see are used by devel/preview/production.cfg
and should not be used directly.

For backgrounds, see this weblog entry and the other documentation it
points to:

http://maurits.vanrees.org/weblog/archive/2008/01/easily-creating-repeatable-buildouts


Now, you need to run:

 $ python2.4 bootstrap.py

This will install the bin/buildout script for you.

To create an instance you now run:

 $ bin/buildout

This will download Plone's eggs and products for you, as well as other
dependencies, create a new Zope 2 installation, and create a new Zope
instance configured with these products.

You can start your Zope instance by running:

 $ bin/instance start

or, to run in foreground mode:

 $ bin/instance fg


Upgrading a preview/production buildout
---------------------------------------

Stop the instance:

 $ bin/instance stop

Make a backup of the Data.fs (database):

 $ bin/repozo --backup --repository=/some/dir --file var/filestorage/Data.fs

where /some/dir is a directory that you choose.

Stop the zeo server (if any):

 $ bin/zeoserver stop

Now switch the buildout to the tag given by Zest, e.g.:

 $ svn switch https://svn.zestsoftware.nl/.../tags/0.1

Run bin/buildout in *upgrade* mode (this will get the new packages):

 $ bin/buildout -nv

Watch for any errors.

Start the zeo server (if any):

 $ bin/zeoserver start

Start the zope instance:

 $ bin/instance start

When varnish is used, restart it:

 $ bin/varnish

Watch for any errors in the instance log file:

 $ tail -f var/log/instance.log

Now you may need to (re)install some products in the Plone Site
control panel.  If unsure, ask Zest Software.



For general comments about using buildout see the file
``buildout.txt`` and http://plone.org/documentation/tutorial/buildout
