# The folder structure is in it's own file now.
from folderstructure import *

GLOBALS = globals()

# Portal Properties
PORTAL_TITLE = 'MiNa-Raad'
EMAIL_FROM_ADDRESS = 'communicatie@minaraad.be'
EMAIL_FROM_NAME = 'Communicatie MiNa-Raad'

# Site Wide Properties
LOCAL_TIME_FORMAT = '%d-%b-%Y'
LOCAL_LONG_TIME_FORMAT = '%d-%b-%Y %H:%M'

DEFAULT_LANGUAGE = 'nl'

DEPENDENCIES = ['kupu','PasswordResetTool','FCKeditor',
                'RichDocument', 'OrderableReferenceField',
                'TextIndexNG3']

STYLESHEETS = [{'id': 'minaraad.css'}]

# MINARAAD_FOLDER_WORKFLOW_TYPES is the list of content types that
# should get the minaraad folder workflow
MINARAAD_FOLDER_WORKFLOW_TYPES = []

LEFT_SLOTS = ( ) 

RIGHT_SLOTS = ('here/portlet_recent/macros/portlet',
               'here/portlet_review/macros/portlet',
              ) 

# Used to show the stringfield 'other country' when in the selectionbox
# 'Ander land' is selected
# And a script for dropdownmenu
JAVASCRIPTS = [{'id': 'hideShow.js'},{'id': 'tabsDropDown.js'}]

# These actions can be found in portal_actions
# and will be disabled
INVISIBLE_ACTIONS = ['rss', 'accessibility', 'plone_setup', 'full_screen']

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

# IDs not to list in the navtree
IDS_NOT_TO_LIST = ['Members','contactpersonen']

# Types to list in the navtree => the rest won't!
TYPES_TO_LIST = ['Folder']

# Titles that shouldn't appear in the navtree even though they are folders
TITLES_NOT_IN_TABS = []

# EXTRA_VIEWS is a dictionary, the keys are portal types.
# The values are a list of templates or page names that are to
# be added in the view dropdown.
EXTRA_VIEWS = {
    'Folder': ['hearing_listing_view', 'advisory_listing_view', 
               'newsletter_listing_view', 'pressrelease_listing_view',
               'study_listing_view','annualreport_listing_view',
               'mrevent_listing_view'],
    }

# SELECT_VIEWS is a dictionary, the keys are folder names. The value
# is the view to be selected for that folder.
SELECT_VIEWS = {
    '/hoorzittingen/hrz_2005': 'hearing_listing_view',
    '/hoorzittingen/hrz_2006': 'hearing_listing_view',
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
    '/studies/std_1999': 'study_listing_view',
    '/studies/std_2000': 'study_listing_view',
    '/studies/std_2001': 'study_listing_view',
    '/studies/std_2002': 'study_listing_view',
    '/studies/std_2003': 'study_listing_view',
    '/studies/std_2005': 'study_listing_view',
    '/studies/std_2006': 'study_listing_view',
    '/jaarverslag': 'annualreport_listing_view',
    '/evenementen': 'mrevent_listing_view',
    }

#FCKeditor set height and width
FCK_FORCE_HEIGHT = '500px'
FCK_FORCE_WIDTH = '568px'


#FCKeditor Toolbar
FCK_TOOLBAR = 'Custom'

FCK_CUSTOM_TOOLBAR = """[['Source', 'DocProps', 'Save', 'NewPage','Preview','Templates', 
    'Cut', 'Copy', 'Paste', 'PasteText','Print', 'PasteWord', 'SpellCheck', 'Undo', 'Redo', 'Find', 'Replace', 'SelectAll', 
    'RemoveFormat', 'Subscript', 'Superscript'],
                         ['Bold', 'Italic','Underline', 'StrikeThrough', 'OrderedList', 'UnorderedList', 'Outdent', 'Indent', 'TextColor','BGColor', 'JustifyLeft', 'JustifyCenter', 'JustifyRight',  'JustifyFull','Link','Unlink','Anchor', 'Image', 'Flash', 'Table', 'Rule', 'Smiley', 'SpecialChar'],
                         ['Style','FontFormat', 'FontName','FontSize'],
                         ['UniversalKey','About']]"""

FCK_MENU_STYLES = '''<Style name="Image on Left" element="img">
            <Attribute name="class" value="img_left" />
        </Style>
        <Style name="Subheader 1" element="span">
            <Attribute name="class" value="subheader1" />
        </Style>
        <Style name="Subheader 2" element="span">
            <Attribute name="class" value="subheader2" />
        </Style>
        <Style name="Subheader 3" element="span">
            <Attribute name="class" value="subheader3" />
        </Style>
        <Style name="Image on Right" element="img">
            <Attribute name="class" value="img_right" />
        </Style>
        <Style name="Image on Left" element="img">
            <Attribute name="class" value="img_left" />
        </Style>
        <Style name="Image on Top" element="img">
            <Attribute name="class" value="img_top" />
        </Style>
        <Style name="Link Plain" element="a">
            <Attribute name="class" value="link-plain" />
        </Style>
        <Style name="Custom Ruler" element="hr">
            <Attribute name="size" value="1" />
            <Attribute name="color" value="#ff0000" />
        </Style>'''

FCK_AREA_STYLE = 'minaraad.css'

# let's cheat a bit and make this available to everyone
from Products.OrderableReferenceField import \
     OrderableReferenceField, OrderableReferenceWidget
