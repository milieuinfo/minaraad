# -*- coding: utf-8 -*-
#
# File: NewsItem.py
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
from Products.minaraad.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='category',
        index="FieldIndex:brains",
        widget=SelectionWidget(
            label='Category',
            label_msgid='minaraad_label_category',
            i18n_domain='minaraad',
        ),
        vocabulary=["Vastgestelde adviezen","Adviezen in wording","Mededelingen","Europese ontwikkelingen"]
    ),

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
        widget=OrderableReferenceWidget(
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson',),
        multiValued=1,
        relationship='newsitem_contact'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

NewsItem_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class NewsItem(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'NewsItem'

    meta_type = 'NewsItem'
    portal_type = 'NewsItem'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = False
    #content_icon = 'NewsItem.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "NewsItem"
    typeDescMsgId = 'description_edit_newsitem'

    _at_rename_after_creation = True

    schema = NewsItem_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(NewsItem, PROJECTNAME)
# end of class NewsItem

##code-section module-footer #fill in your manual code here
##/code-section module-footer



