# -*- coding: utf-8 -*-
__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.minaraad.PostMixin import PostMixin
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.config import *

schema = Schema((

    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    # The summary field is called 'body' to be consistent with Advisory.
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

    DateTimeField(
        name='date',
        widget=CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        ),
        required=1
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
        relationship='study_contact'
    ),

),
)


Study_schema = getattr(PostMixin, 'schema', Schema(())).copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    getattr(Attachmentsmixin, 'schema', Schema(())).copy() + \
    schema.copy()


class Study(PostMixin, EmailMixin, Attachmentsmixin):
    """
    A study
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PostMixin,'__implements__',()),) + (getattr(EmailMixin,'__implements__',()),) + (getattr(Attachmentsmixin,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Study'

    meta_type = 'Study'
    portal_type = 'Study'
    allowed_content_types = [] + list(getattr(PostMixin, 'allowed_content_types', [])) + list(getattr(EmailMixin, 'allowed_content_types', [])) + list(getattr(Attachmentsmixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'Study.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Study"
    typeDescMsgId = 'description_edit_study'

    actions =  (
       {'action': "string:${object_url}/email_out",
        'category': "object",
        'id': 'email_out',
        'name': 'E-mail',
        'permissions': ("Modify portal content",),
        'condition': 'python:1'
       },
       {'action': "string:${object_url}/export_subscribers",
        'category': "object",
        'id': 'export_subscribers',
        'name': 'Export Subscribers',
        'permissions': ("Modify portal content",),
        'condition': 'python:1'
       },
    )

    _at_rename_after_creation = True
    schema = Study_schema


registerType(Study, PROJECTNAME)
