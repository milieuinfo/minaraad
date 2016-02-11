# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.CMFPlone.interfaces import INonStructuralFolder
from zope.interface import implements
from Products.SimpleAttachment.widget import AttachmentsManagerWidget

schema = atapi.Schema((
    atapi.BooleanField(
        name='displayAttachments',
        widget=AttachmentsManagerWidget(
            label='Displayattachments',
            label_msgid='minaraad_label_displayAttachments',
            i18n_domain='minaraad',
        )
    ),
),
)

Attachmentsmixin_schema = atapi.OrderedBaseFolderSchema.copy() + \
    schema.copy()


class Attachmentsmixin(atapi.OrderedBaseFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(INonStructuralFolder,)

    # This name appears in the 'add' box
    archetype_name = 'Attachmentsmixin'

    meta_type = 'Attachmentsmixin'
    portal_type = 'Attachmentsmixin'
    allowed_content_types = ['FileAttachment']
    filter_content_types = 1
    global_allow = 0
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Attachmentsmixin"
    typeDescMsgId = 'description_edit_attachmentsmixin'

    _at_rename_after_creation = True

    schema = Attachmentsmixin_schema

    def get_first_image(self):
        """ Return first image attached to this content item
        """
        images = self.get_images()
        if len(images) > 0:
            return images[0]

    def has_image(self):
        """ Return True if we find a first image.
        """
        if self.get_first_image() is not None:
            return True
        return False

    def get_images(self):
        """ return a list of images attached to this content item
        """
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog.searchResults(
            portal_type='ImageAttachment',
            path={'query': '/'.join(self.getPhysicalPath()),
                  'depth': 1},
            sort_on='getObjPositionInParent')
        return [brain.getObject() for brain in brains]

    def get_attachments(self):
        """ return a list of images attached to this item
        """
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog.searchResults(
            portal_type='FileAttachment',
            path={'query': '/'.join(self.getPhysicalPath()),
                  'depth': 1},
            sort_on='getObjPositionInParent')
        return [brain.getObject() for brain in brains]

    def SearchableText(self, **kwargs):
        """ Add the contents of SearchableText to the Advise
        """
        result = super(atapi.OrderedBaseFolder, self).SearchableText()
        for attachment in self.get_attachments():
            result += attachment.SearchableText()
        return result
