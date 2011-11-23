# -*- coding: utf-8 -*-
__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
from Products.minaraad.config import *

from Products.SimpleAttachment.widget import AttachmentsManagerWidget

schema = Schema((
    BooleanField(
        name='displayAttachments',
        widget=AttachmentsManagerWidget(
            label='Displayattachments',
            label_msgid='minaraad_label_displayAttachments',
            i18n_domain='minaraad',
        )
    ),
),
)

Attachmentsmixin_schema = BaseFolderSchema.copy() + \
    schema.copy()


class Attachmentsmixin(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),) + (INonStructuralFolder,)

    # This name appears in the 'add' box
    archetype_name = 'Attachmentsmixin'

    meta_type = 'Attachmentsmixin'
    portal_type = 'Attachmentsmixin'
    allowed_content_types = ['FileAttachment']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'Attachmentsmixin.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Attachmentsmixin"
    typeDescMsgId = 'description_edit_attachmentsmixin'

    _at_rename_after_creation = True

    schema = Attachmentsmixin_schema

    def SearchableText(self, **kwargs):
        result = super(BaseFolder, self).SearchableText()
        for attachment in self.contentValues(
            filter=dict(portal_type='FileAttachment')):
            result += attachment.SearchableText()
        return result


registerType(Attachmentsmixin, PROJECTNAME)