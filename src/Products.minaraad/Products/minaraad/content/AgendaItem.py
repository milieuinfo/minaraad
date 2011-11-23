# -*- coding: utf-8 -*-
#
# File: AgendaItem.py
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
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.config import *

from minaraad.projects.content.base_agendaitem import base_agendaitem_schema, BaseAgendaItem

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='speaker',
        widget=StringWidget(
            label='Speaker',
            label_msgid='minaraad_label_speaker',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    StringField(
        name='organisation',
        widget=StringWidget(
            label='Organisation',
            label_msgid='minaraad_label_organisation',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    TextField(
        name='summary',
        widget=TextAreaWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            i18n_domain='minaraad',
        )
    ),

    DateTimeField(
        name='itemstartdate',
        widget=CalendarWidget(
            visible=False
        ),
        required=False
    ),

    DateTimeField(
        name='itemenddate',
        widget=CalendarWidget(
            visible=False,
        ),
        required=False
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

AgendaItem_schema = getattr(Attachmentsmixin, 'schema', Schema(())).copy() + \
                    base_agendaitem_schema.copy() + \
                    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class AgendaItem(Attachmentsmixin, BaseAgendaItem):
    """
    An Agendaitem
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Attachmentsmixin,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'AgendaItem'

    meta_type = 'AgendaItem'
    portal_type = 'AgendaItem'
    allowed_content_types = [] + list(getattr(Attachmentsmixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    #content_icon = 'AgendaItem.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "AgendaItem"
    typeDescMsgId = 'description_edit_agendaitem'

    _at_rename_after_creation = True

    schema = AgendaItem_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(AgendaItem, PROJECTNAME)
# end of class AgendaItem

##code-section module-footer #fill in your manual code here
##/code-section module-footer


