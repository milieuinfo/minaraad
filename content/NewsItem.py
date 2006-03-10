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
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='category',
        widget=SelectionWidget(
            label='Category',
            label_msgid='minaraad_label_category',
            i18n_domain='minaraad',
        ),
        vocabulary=["Vastgestelde adviezen","Adviezen in wording","Mededelingen","Europese ontwikkelingen"]
    ),

    ReferenceField(
        name='contactpersons',
        widget=ReferenceWidget(
            label='Contactpersons',
            label_msgid='minaraad_label_contactpersons',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson',),
        multiValued=0,
        relationship='newsitem_contactperson'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

NewsItem_schema = BaseSchema.copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class NewsItem(EmailMixin, BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(EmailMixin,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'NewsItem'

    meta_type = 'NewsItem'
    portal_type = 'NewsItem'
    allowed_content_types = [] + list(getattr(EmailMixin, 'allowed_content_types', []))
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



