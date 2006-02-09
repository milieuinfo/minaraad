# File: AgendaItems.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.1 svn/devel
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
        name='speaker',
        widget=StringWidget(
            label='Speaker',
            label_msgid='minaraad_label_speaker',
            i18n_domain='minaraad',
        )
    ),

    StringField(
        name='summary',
        widget=StringWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            i18n_domain='minaraad',
        )
    ),

    IntegerField(
        name='starthour',
        widget=SelectionWidget(
            label='Starthour',
            label_msgid='minaraad_label_starthour',
            i18n_domain='minaraad',
        ),
        vocabulary=[7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    ),

    IntegerField(
        name='startminutes',
        widget=IntegerWidget(
            label='Startminutes',
            label_msgid='minaraad_label_startminutes',
            i18n_domain='minaraad',
        )
    ),

    IntegerField(
        name='endhour',
        widget=SelectionWidget(
            label='Endhour',
            label_msgid='minaraad_label_endhour',
            i18n_domain='minaraad',
        ),
        vocabulary=[7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    ),

    IntegerField(
        name='endminutes',
        widget=IntegerWidget(
            label='Endminutes',
            label_msgid='minaraad_label_endminutes',
            i18n_domain='minaraad',
        )
    ),

    FileField(
        name='attachment',
        widget=FileWidget(
            label='Attachment',
            label_msgid='minaraad_label_attachment',
            i18n_domain='minaraad',
        ),
        storage=AttributeStorage(),
        multiValued=True
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

AgendaItems_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class AgendaItems(BaseContent):
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name = 'AgendaItems'

    meta_type = 'AgendaItems'
    portal_type = 'AgendaItems'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = False
    #content_icon = 'AgendaItems.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "AgendaItems"
    typeDescMsgId = 'description_edit_agendaitems'

    _at_rename_after_creation = True

    schema = AgendaItems_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # Methods

registerType(AgendaItems,PROJECTNAME)
# end of class AgendaItems

##code-section module-footer #fill in your manual code here
##/code-section module-footer



