# -*- coding: utf-8 -*-
__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget

from Products.minaraad.PostMixin import PostMixin
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.config import *

schema = Schema((

    DateTimeField(
        name='date',
        index="DateIndex:brains",
        widget=CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        )
    ),

    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    # Body (which already existed) serves as the summary (of the attachment,
    # summary is shown in the listings).
    TextField(
        name='body',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            i18n_domain='minaraad',
        ),
        default_output_type='text/html'
    ),

    OrderableReferenceField(
        name='contact',
        vocabulary_display_path_bound="-1",
        widget=OrderableReferenceWidget(
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson',),
        multiValued=1,
        relationship='advisory_contact'
    ),

    ReferenceField(
        name='relatedDocuments',
        vocabulary_display_path_bound="-1",
        widget=ReferenceBrowserWidget(
            label='Related Documents',
            label_msgid='minaraad_label_related_documents',
            description = "Related and published digibib documents and files",
            description_msgid = "minaraad_help_related_documents",
            i18n_domain='minaraad',
            # ATReferenceBrowser specific additions:
            startup_directory = 'digibib-1/dossiers-adviezen',
            restrict_browsing_to_startup_directory = 0,
            only_for_review_states = ('published', ),
            show_review_state = 1,
            allow_search = 1,
            allow_browse = 1,
            show_indexes = 0,
            force_close_on_insert = 0,
        ),
        index = 'KeywordIndex',
        allowed_types=('Document', 'File'),
        multiValued=True,
        relationship='related_documents'
    ),
),
)

Advisory_schema = getattr(PostMixin, 'schema', Schema(())).copy() + \
    getattr(Attachmentsmixin, 'schema', Schema(())).copy() + \
    schema.copy()
Advisory_schema['description'].isMetadata = False


class Advisory(PostMixin, Attachmentsmixin):
    """An advisory
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PostMixin,'__implements__',()),) + (getattr(Attachmentsmixin,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Advisory'

    meta_type = 'Advisory'
    portal_type = 'Advisory'
    allowed_content_types = [] + list(getattr(PostMixin, 'allowed_content_types', [])) + list(getattr(Attachmentsmixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'Advisory.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Advisory"
    typeDescMsgId = 'description_edit_advisory'

    actions =  (
       {'action': "string:${object_url}/export_subscribers",
        'category': "object",
        'id': 'export_subscribers',
        'name': 'Export Subscribers',
        'permissions': ("Modify portal content",),
        'condition': 'python:1'
       },
    )
    _at_rename_after_creation = True
    schema = Advisory_schema


registerType(Advisory, PROJECTNAME)
