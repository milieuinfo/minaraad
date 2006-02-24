# The folder structure is in it's own file now.
from folderstructure import *

DEPENDENCIES = ['PasswordResetTool', 'CompoundField']

STYLESHEETS = [{'id': 'minaraad.css'}]

# NOT_INTERNET_WORFKLOW_TYPES is the list of content types that don't
# need to get the minaraad_workflow workflow.
NOT_INTERNET_WORFKLOW_TYPES = ['Plone Site',
                               'PloneFormMailer']

# INTERNET_FOLDER_WORKFLOW_TYPES is the list of content types that
# shouldn't get the minaraad_workflow workflow
INTERNET_FOLDER_WORKFLOW_TYPES = ['']

LEFT_SLOTS = ('here/portlet_navigation/macros/portlet',
              'here/portlet_personalbar/macros/portlet',
              ) 

# Used to show the stringfield 'other country' when in the selectionbox
# 'Ander land' is selected
JAVASCRIPTS = [{'id': 'hideShow.js'},]

# GLOBAL_DISALLOW is a list of content types that will be disabled
# on the portal root and on all subfolders.
GLOBAL_DISALLOW = [
    'ContactPerson',
    'Advisory',
    'Newsitem',
    'Event',
    ]

# In 'folder', restrict addable types to 'restriction'
LOCAL_ADDITIONS = {
    'hoorzittingen': ['Hearing'],
    }

# IDs not to list in the navtree
IDS_NOT_TO_LIST = ['Members','contactpersonen']

# Types to list in the navtree => the rest won't!
TYPES_TO_LIST = ['Folder']

# EXTRA_VIEWS is a dictionary, the keys are portal types.
# The values are a list of templates or page names that are to
# be added in the view dropdown.
EXTRA_VIEWS = {
    'Folder': ['hearing_listing_view'],
    }

# SELECT_VIEWS is a dictionary, the keys are folder names. The value
# is the view to be selected for that folder.
SELECT_VIEWS = {
    '/hoorzittingen': 'hearing_listing_view',
    }

# Kupu Configuration LINKABLE is a list of content types to which we
# can link within the kupu drawer
LINKABLE = ['Hearing',
            'Advisory',
            'AnnualReport',
            'Newsitem',
            'NewsLetter',
            'Pressrelease',
            'Study',
            'Event',
           ]