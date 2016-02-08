# -*- coding: utf-8 -*-
from zope.interface import implements
from zExceptions import Unauthorized
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.CMFCore.utils import getToolByName
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget
from plone.app.blob.field import ImageField

from Products.minaraad.interfaces import IAdvisory
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.ImageAttachmentsmixin import ImageAttachmentsmixin
from Products.minaraad.PostMixin import PostMixin
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.ThemeMixin import ThemeMixin
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.content.themes import ThemeMixin as OldThemeMixin
from Products.minaraad.content.themes import theme_schema
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.content.contacts import contacts_schema

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

    # Body (which already existed) serves as the summary (of the attachment,
    # summary is shown in the listings).
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
            startup_directory='digibib/projects',
            restrict_browsing_to_startup_directory=0,
            only_for_review_states=('published', ),
            show_review_state=1,
            allow_search=1,
            allow_browse=1,
            show_indexes=0,
            force_close_on_insert=0,
        ),
        allowed_types=('Document', 'File', 'FileAttachment'),
        multiValued=True,
        relationship='related_documents'
    ),

    atapi.ReferenceField(
        name='project',
        allowed_types=('Project'),
        multiValued=False,
        relationship='related_project',
    ),
),
)

Advisory_schema = (
    getattr(PostMixin, 'schema', atapi.Schema(())).copy() +
    getattr(EmailMixin, 'schema', atapi.Schema(())).copy() +
    theme_schema.copy() +
    getattr(Attachmentsmixin, 'schema', atapi.Schema(())).copy() +
    getattr(ImageAttachmentsmixin, 'schema', atapi.Schema(())).copy() +
    contacts_schema.copy() +
    schema.copy())
Advisory_schema['description'].isMetadata = False
# Hide the description field.
Advisory_schema['description'].widget.visible = {
    'edit': 'hidden', 'view': 'invisible'}
Advisory_schema['project'].widget.visible = {
    'edit': 'invisible', 'view': 'invisible'}

Advisory_schema.moveField('coordinator', after="foto")
Advisory_schema.moveField('authors', after="coordinator")


class Advisory(Attachmentsmixin, PostMixin, OldThemeMixin, ThemeMixin, EmailMixin):
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
        res = []
        docs = self.getField('relatedDocuments').get(self)
        if not docs:
            return res
        mtool = getToolByName(self, 'portal_membership')
        for d in range(len(docs)):
            try:
                obj = docs[d]
            except Unauthorized:
                continue
            if obj not in res:
                if mtool.checkPermission('View', obj):
                    res.append(obj)
        return res


atapi.registerType(Advisory, PROJECTNAME)
