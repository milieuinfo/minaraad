# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles

# The folder structure is in it's own file now.
from folderstructure import *


PROJECTNAME = "minaraad"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer.
# In the Products namespace:
PRODUCT_DEPENDENCIES = ['OrderableReferenceField',
                        'SimpleAttachment', 'DataGridField']
# Note that minaraad.projects must be installed after
# SimpleAttachment, as it changes its type information in portal_types
# a bit.
#
# Other dependency packages:
PACKAGE_DEPENDENCIES = ['minaraad.projects']


# This is used for the gender field in portal_memberdata
TITLE_VOCAB = ['', 'De heer', 'Mevrouw', 'Juffrouw', 'Monsieur', 'Madame',
               'Madamoiselle', 'Ing.', 'Ir.', 'Dr.',
               'Dr. Ir.', 'Prof.', 'Prof. Dr.', 'Prof. Dr. Ir.', 'Em. Prof.',
               'Dir. Ir.', 'Em. Prof. Dr.']

# recaptcha settings.  See
# http://pypi.python.org/pypi/collective.recaptcha and
# http://recaptcha.net/
# Keys created by Maurits, valid for *.minaraad.be (and *.zestsoftware.nl)
RECAPTCHA_PUBLIC_KEY = '6LdBxwsAAAAAAIBbpW6qkPKTHxL8FJ8D523A9WE3'
RECAPTCHA_PRIVATE_KEY = '6LdBxwsAAAAAAK-gNRxTL6XljgfZ183TvR8rpQxw'
