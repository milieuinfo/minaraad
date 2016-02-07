# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFPlone.interfaces import INonStructuralFolder
from zope.interface import implements
from Products.SimpleAttachment.widget import AttachmentsManagerWidget

from Products.minaraad.config import PROJECTNAME

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

    def getFirstImage(self):
        """ Return first image attached to this content item
        """
        images = self.getImages()
        if len(images) > 0:
            return images[0]

    def has_image(self):
        if self.getFirstImage() is not None:
            return True
        return False

    def getImages(self):
        """ return a list of images attached to this content item
        """
        return self.contentValues(filter=dict(portal_type='ImageAttachment'))


    def getAttachments(self):
        """ return a list of images attached to this item
        """
        return self.contentValues(filter=dict(portal_type='FileAttachment'))

    def SearchableText(self, **kwargs):
        result = super(atapi.OrderedBaseFolder, self).SearchableText()
        for attachment in self.getAttachments():
            result += attachment.SearchableText()
        return result


atapi.registerType(Attachmentsmixin, PROJECTNAME)
