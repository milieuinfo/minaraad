# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.minaraad import MinaraadMessageFactory as _
from Products.SimpleAttachment.widget import ImagesManagerWidget
from zope.interface import implements


schema = atapi.Schema((
    atapi.BooleanField(
        name='displayImages',
        widget=ImagesManagerWidget(
            label=_(u'minaraad_label_displayImages',
                    default=u'Display images'),
        )
    ),
),
)

ImageAttachmentsmixin_schema = atapi.OrderedBaseFolderSchema.copy() + \
    schema.copy()


class ImageAttachmentsmixin(atapi.OrderedBaseFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(INonStructuralFolder,)

    # This name appears in the 'add' box
    archetype_name = 'ImageAttachmentsmixin'

    meta_type = 'ImageAttachmentsmixin'
    portal_type = 'ImageAttachmentsmixin'
    allowed_content_types = ['ImageAttachment']
    filter_content_types = 1
    global_allow = 0
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "ImageAttachmentsmixin"
    typeDescMsgId = 'description_edit_imageattachmentsmixin'

    _at_rename_after_creation = True

    schema = ImageAttachmentsmixin_schema
