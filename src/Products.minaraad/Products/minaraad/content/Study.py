# -*- coding: utf-8 -*-
from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget
from plone.app.blob.field import ImageField

from Products.minaraad.PostMixin import PostMixin
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.content.themes import ThemeMixin
from Products.minaraad.content.themes import theme_schema

from Products.minaraad.interfaces import IStudy
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.content.contacts import contacts_schema

schema = atapi.Schema((

    atapi.TextField(
        name='description',
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    # The summary field is called 'body' to be consistent with Advisory.
    atapi.TextField(
        name='body',
        allowable_content_types=('text/html', 'text/plain', 'text/structured',
                                 'application/msword', ),
        widget=atapi.RichWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            i18n_domain='minaraad',
        ),
        default_content_type='text/html',
        default_output_type='text/html',
    ),

    ImageField(
        name='foto',
        widget=atapi.ImageWidget(
            label="Photo",
            label_msgid='minaraad_label_foto',
            i18n_domain='minaraad',
        ),
        storage=atapi.AttributeStorage(),
        sizes={'foto': (300, 300)}
    ),

    atapi.DateTimeField(
        name='date',
        widget=atapi.CalendarWidget(
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
            visible=False,
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson', ),
        multiValued=1,
        relationship='study_contact'
    ),
),
)


Study_schema = getattr(PostMixin, 'schema', atapi.Schema(())).copy() + \
    getattr(EmailMixin, 'schema', atapi.Schema(())).copy() + \
    getattr(Attachmentsmixin, 'schema', atapi.Schema(())).copy() + \
    theme_schema.copy() + \
    schema.copy() + \
    contacts_schema.copy()


class Study(PostMixin, EmailMixin, ThemeMixin, Attachmentsmixin):
    """
    A study
    """
    implements(IStudy, IUseContact)
    security = ClassSecurityInfo()
    archetype_name = 'Study'
    portal_type = 'Study'
    _at_rename_after_creation = True
    schema = Study_schema


atapi.registerType(Study, PROJECTNAME)
