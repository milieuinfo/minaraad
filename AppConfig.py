# The folder structure is in it's own file now.
from folderstructure import *

# Portal Properties
PORTAL_TITLE = 'MiNa-Raad'
EMAIL_FROM_ADDRESS = 'postmaster@zestsoftware.nl'
EMAIL_FROM_NAME = 'Webmaster MiNa-Raad'

# Site Wide Properties
LOCAL_TIME_FORMAT = '%d-%b-%Y'
LOCAL_LONG_TIME_FORMAT = '%d-%b-%Y %H:%M'

DEFAULT_LANGUAGE = 'nl'

DEPENDENCIES = ['kupu','PasswordResetTool','FCKeditor',
                'RichDocument', 'OrderableReferenceField']

STYLESHEETS = [{'id': 'minaraad.css'}]

# MINARAAD_FOLDER_WORKFLOW_TYPES is the list of content types that
# should get the minaraad folder workflow
MINARAAD_FOLDER_WORKFLOW_TYPES = []

LEFT_SLOTS = ('here/portlet_navigation/macros/portlet',
#              'here/portlet_personalbar/macros/portlet',
              'here/portlet_login/macros/portlet',
              ) 

RIGHT_SLOTS = ('here/portlet_review/macros/portlet',
               'here/portlet_events/macros/portlet',
              ) 

# Used to show the stringfield 'other country' when in the selectionbox
# 'Ander land' is selected
JAVASCRIPTS = [{'id': 'hideShow.js'},]

# GLOBAL_DISALLOW is a list of content types that will be disabled
# on the portal root and on all subfolders.
GLOBAL_DISALLOW = [
    'Newsitem',
    'RichDocument',
    ]

ADD_LIST = ['Folder',
            'File',
            'Document',
            'Link',
            'Image',
            'Event',
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
    'evenementen': ADD_LIST,
    }

# IDs not to list in the navtree
IDS_NOT_TO_LIST = ['Members','contactpersonen']

# Types to list in the navtree => the rest won't!
TYPES_TO_LIST = ['Folder']

# EXTRA_VIEWS is a dictionary, the keys are portal types.
# The values are a list of templates or page names that are to
# be added in the view dropdown.
EXTRA_VIEWS = {
    'Folder': ['hearing_listing_view', 'advisory_listing_view', 
               'newsletter_listing_view', 'pressrelease_listing_view',
               'study_listing_view'],
    }

# SELECT_VIEWS is a dictionary, the keys are folder names. The value
# is the view to be selected for that folder.
SELECT_VIEWS = {
    '/hoorzittingen': 'hearing_listing_view',
    '/nieuwsbrieven/newsl_2006': 'newsletter_listing_view',
    '/nieuwsbrieven/newsl_2005': 'newsletter_listing_view',
    '/nieuwsbrieven/newsl_2004': 'newsletter_listing_view',
    '/nieuwsbrieven/newsl_2003': 'newsletter_listing_view',
    '/adviezen/adv_2006': 'advisory_listing_view',
    '/adviezen/adv_2005': 'advisory_listing_view',
    '/adviezen/adv_2004': 'advisory_listing_view',
    '/adviezen/adv_2003': 'advisory_listing_view',
    '/adviezen/adv_2002': 'advisory_listing_view',
    '/adviezen/adv_2001': 'advisory_listing_view',
    '/adviezen/adv_1999': 'advisory_listing_view',
    '/persberichten/pressr_2006' : 'pressrelease_listing_view',
    '/persberichten/pressr_2005' : 'pressrelease_listing_view',
    '/persberichten/pressr_2004' : 'pressrelease_listing_view',
    '/persberichten/pressr_2003' : 'pressrelease_listing_view',
    '/persberichten/pressr_2002' : 'pressrelease_listing_view',
    '/studies': 'study_listing_view',
    }

#FCKeditor set height
FCK_FORCE_HEIGHT = '500px'


#FCKeditor Toolbar
FCK_TOOLBAR = 'Custom'

FCK_CUSTOM_TOOLBAR = """[['Source', 'DocProps', 'Save', 'NewPage','Preview','Templates', 
    'Cut', 'Copy', 'Paste', 'PasteText','Print', 'PasteWord', 'SpellCheck', 'Undo', 'Redo', 'Find', 'Replace', 'SelectAll', 
    'RemoveFormat', 'Bold', 'Italic', 'Underline', 'StrikeThrough', 'Subscript', 
    'Superscript', 'OrderedList', 'UnorderedList', 'Outdent', 'Indent'],
                         ['Style','FontFormat', 'FontName','FontSize','TextColor','BGColor', 'JustifyLeft', 'JustifyCenter', 
    'JustifyRight', 'JustifyFull'],
                         ['Link','Unlink','Anchor', 'Image', 'Flash', 'Table', 'Rule', 'Smiley', 'SpecialChar', 
    'UniversalKey','About']]"""

# let's cheat a bit and make this available to everyone
from Products.OrderableReferenceField import \
     OrderableReferenceField, OrderableReferenceWidget
