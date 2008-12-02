# -*- coding: utf-8 -*-
__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
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

    # TODO: Add rich text description, but body is already there...

    TextField(
        name='body',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Body',
            label_msgid='minaraad_label_body',
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
