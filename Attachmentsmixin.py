# -*- coding: utf-8 -*-
#
# File: Attachmentsmixin.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.5.0 svn/devel
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
from Products.minaraad.config import *

# additional imports from tagged value 'import'
from Products.RichDocument.widget import AttachmentsManagerWidget

##code-section module-header #fill in your manual code here
##/code-section module-header

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

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Attachmentsmixin_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

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
    allow_discussion = False
    #content_icon = 'Attachmentsmixin.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Attachmentsmixin"
    typeDescMsgId = 'description_edit_attachmentsmixin'

    _at_rename_after_creation = True

    schema = Attachmentsmixin_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Attachmentsmixin, PROJECTNAME)
# end of class Attachmentsmixin

##code-section module-footer #fill in your manual code here
##/code-section module-footer



