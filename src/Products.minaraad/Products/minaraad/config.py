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
PRODUCT_DEPENDENCIES = ['FCKeditor', 'OrderableReferenceField',
                        'SimpleAttachment']
# Note that minaraad.projects must be installed after
# SimpleAttachment, as it changes its type information in portal_types
# a bit.
#
# Other dependency packages:
PACKAGE_DEPENDENCIES = ['collective.emaillogin', 'minaraad.projects']

ADD_LIST = ['Folder',
            'File',
            'Document',
            'Link',
            'Image',
            'Topic',
            ]

# In 'folder', restrict addable types to 'restriction'
LOCAL_ADDITIONS = {
    'hoorzittingen': ['Hearing'],
    'adviezen': ['Advisory'],
    'nieuwsbrieven': ['NewsLetter'],
    'persberichten': ['Pressrelease'],
    'jaarverslag': ['AnnualReport'],
    'studies': ['Study'],
    'contactpersonen': ['ContactPerson'],
    'voorstelling': ADD_LIST,
    'evenementen': ['MREvent'],
    }

# SELECT_VIEWS is a dictionary, the keys are folder names. The value
# is the view to be selected for that folder.
SELECT_VIEWS = {
    'jaarverslag': 'annualreport_listing_view',
    'evenementen': 'mrevent_listing_view',
    'voorstelling': 'mina_listing',
    'adviezen': 'mina_listing',
    'nieuwsbrieven': 'mina_listing',
    'persberichten': 'mina_listing',
    'studies': 'mina_listing',
    'hoorzittingen': 'mina_listing',
    'contactpersonen': 'list_contact_persons',
    }


# INITIAL_CHILD_LAYOUT is a dictionary, the keys are folder names. The
# value is the view to be selected for the *children* of that folder
# (as long as those children are folders themselves).
INITIAL_CHILD_LAYOUT = {
    'adviezen': 'advisory_listing_view',
    'nieuwsbrieven': 'newsletter_listing_view',
    'persberichten': 'pressrelease_listing_view',
    'studies': 'study_listing_view',
    'hoorzittingen': 'hearing_listing_view',
    }


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
