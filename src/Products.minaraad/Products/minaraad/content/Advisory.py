# -*- coding: utf-8 -*-
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget
from plone.app.blob.field import ImageField

from Products.minaraad import MinaraadMessageFactory as _
from Products.minaraad.interfaces import IAdvisory
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.ImageAttachmentsmixin import ImageAttachmentsmixin
from Products.minaraad.ThemeMixin import ThemeParentMixin
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.content.contacts import contacts_schema
from Products.minaraad.utils import list_viewable

# Do NOT import this as underscore, as i18ndude will then pick it up
# for the wrong domain.
from minaraad.projects import MinaraadProjectMessageFactory

schema = atapi.Schema((

    atapi.DateTimeField(
        name='date',
        required=True,
        widget=atapi.CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        )
    ),

    atapi.TextField(
        name='description',
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    atapi.StringField(
        name='product_number',
        required=False,
        validators=('projectNumber3Digits', ),
        widget=atapi.StringWidget(
            label=MinaraadProjectMessageFactory(
                u'label_product_number',
                default=u'Product number')
        )
    ),

    atapi.TextField(
        name='popular_summary',
        allowable_content_types=('text/html', 'text/plain'),
        widget=atapi.RichWidget(
            label=_('Popular summary'),
        ),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
    ),

    # Body (which already existed) serves as the summary (of the attachment,
    # summary is shown in the listings).
    atapi.TextField(
        name='body',
        allowable_content_types=('text/html', 'text/plain'),
        widget=atapi.RichWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            i18n_domain='minaraad',
        ),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
    ),
    # Deprecated, can be removed after the final release
    ImageField(
        name='foto',
        widget=atapi.ImageWidget(
            label="Photo",
            label_msgid='minaraad_label_foto',
            i18n_domain='minaraad',
            visible=False
        ),
        storage=atapi.AttributeStorage(),
        sizes={'foto': (300, 300)},

    ),

    OrderableReferenceField(
        name='contact',
        vocabulary_display_path_bound="-1",
        widget=OrderableReferenceWidget(
            visible=False,
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
            base_query={
                'sort_on': 'sortable_title',
            },
        ),
        allowed_types=('ContactPerson', ),
        multiValued=1,
        relationship='advisory_contact'
    ),

    atapi.ReferenceField(
        name='relatedDocuments',
        vocabulary_display_path_bound="-1",
        widget=ReferenceBrowserWidget(
            label='Related Documents',
            label_msgid='minaraad_label_related_documents',
            description="Related and published digibib documents and files",
            description_msgid="minaraad_help_related_documents",
            i18n_domain='minaraad',
            # ATReferenceBrowser specific additions:
            startup_directory='/',
            restrict_browsing_to_startup_directory=0,
            only_for_review_states=('published', ),
            show_review_state=1,
            allow_search=1,
            allow_browse=1,
            show_indexes=0,
            force_close_on_insert=0,
        ),
        allowed_types=('Document', 'File', 'FileAttachment',
                       'Advisory', 'Study', 'MREvent'),
        multiValued=True,
        relationship='related_documents'
    ),

    atapi.ReferenceField(
        name='project',
        allowed_types=('Project',),
        multiValued=False,
        relationship='related_project',
    ),
),
)

Advisory_schema = (
    getattr(Attachmentsmixin, 'schema', atapi.Schema(())).copy() +
    getattr(ImageAttachmentsmixin, 'schema', atapi.Schema(())).copy() +
    schema.copy() +
    contacts_schema.copy()
)
Advisory_schema['description'].isMetadata = False
# Hide the description field.
Advisory_schema['description'].widget.visible = {
    'edit': 'hidden', 'view': 'invisible'}
Advisory_schema['project'].widget.visible = {
    'edit': 'invisible', 'view': 'invisible'}

Advisory_schema.moveField('displayAttachments', after="body")
Advisory_schema.moveField('displayImages', after='displayAttachments')
Advisory_schema.moveField('coordinator', after="displayImages")
Advisory_schema.moveField('authors', after="coordinator")


class Advisory(Attachmentsmixin, ThemeParentMixin):
    """An advisory
    """
    implements(IAdvisory, IUseContact)
    security = ClassSecurityInfo()
    archetype_name = 'Advisory'
    portal_type = 'Advisory'
    _at_rename_after_creation = True
    schema = Advisory_schema

    def getRelatedDocuments(self):
        """Get the documents from the relatedDocuments field.

        Only get those that the user is allowed to access.

        Adapted from
        Products/CMFPlone/skins/plone_scripts/computeRelatedItems.py
        """
        docs = self.getField('relatedDocuments').get(self)
        return list_viewable(docs)


atapi.registerType(Advisory, PROJECTNAME)
