import logging
import os
from ZConfig.components.logger.loghandler import FileHandler as ZopeFileHandler

# Arrange logging of email info, for use by other modules.
email_logger = logging.getLogger('minaraad_email')
# Also log these messages to a separate file
# XXX this may be possible through zope.conf too but I can't figure out
logbase = os.environ.get('MINARAAD_LOG_PATH')
if not logbase:
    # This at least happens when running bin/test in Plone 4...
    # Let's try the current directory, which would then be .../parts/test.
    logbase = os.getcwd()
logpath = '%s/minaraad_email.log' % logbase
# Get rid of any duplicate slashes:
logpath = os.path.realpath(logpath)
# Use Zope FileHandler, as that supports reopening the log file after
# a logrote, when triggered by a SIGUSR2 signal.  See also
# Products/minaraad/__init__.py
hdlr = ZopeFileHandler(logpath)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
email_logger.addHandler(hdlr)


def list_match(l1, l2):
    """ Tells if at least there is one common element
    in the two lists.

    >>> list_match([], [])
    False

    >>> list_match([], ['a', 'b', 'c'])
    False

    >>> list_match(['a', 'b', 'c'], [])
    False

    >>> list_match(['a', 'b', 'c'], ['d', 'e', 'f'])
    False

    >>> list_match(['a', 'b', 'c'], ['d', 'e', 'f', 'b'])
    True

    """
    for el in l1:
        if el in l2:
            return True
    return False
