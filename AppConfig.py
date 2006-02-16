DEPENDENCIES = ['PasswordResetTool']

STYLESHEETS = [{'id': 'minaraad.css'}]

# NOT_INTERNET_WORFKLOW_TYPES is the list of content types that don't
# need to get the minaraad_workflow workflow.
NOT_INTERNET_WORFKLOW_TYPES = ['Plone Site',
                               'PloneFormMailer']

# INTERNET_FOLDER_WORKFLOW_TYPES is the list of content types that
# shouldn't get the minaraad_workflow workflow
INTERNET_FOLDER_WORKFLOW_TYPES = ['']

# Used to show the stringfield 'other country' when in the selectionbox
# 'Ander land' is selected
JAVASCRIPTS = [{'id': 'hideShow.js'},
               ]
