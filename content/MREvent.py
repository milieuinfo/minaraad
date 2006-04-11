# -*- coding: utf-8 -*-
#
# File: MREvent.py
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
from zope.interface import implements, Interface
##/code-section module-header

schema = Schema((

    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    StringField(
        name='subheader',
        widget=StringWidget(
            label='Subheader',
            label_msgid='minaraad_label_subheader',
            i18n_domain='minaraad',
        )
    ),

    TextField(
        name='goal',
        widget=TextAreaWidget(
            label='Goal',
            label_msgid='minaraad_label_goal',
            i18n_domain='minaraad',
        )
    ),

    StringField(
        name='location',
        widget=StringWidget(
            label='Location',
            label_msgid='minaraad_label_location',
            i18n_domain='minaraad',
        )
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

    DateTimeField(
        name='startdate',
        index="DateIndex:brains",
        widget=CalendarWidget(
            label='Startdate',
            label_msgid='minaraad_label_startdate',
            i18n_domain='minaraad',
        ),
        required=1
    ),

    DateTimeField(
        name='enddate',
        widget=CalendarWidget(
            label='Enddate',
            label_msgid='minaraad_label_enddate',
            i18n_domain='minaraad',
        ),
        required=1
    ),

    ImageField(
        name='foto',
        widget=ImageWidget(
            label="Photo",
            label_msgid='minaraad_label_foto',
            i18n_domain='minaraad',
        ),
        storage=AttributeStorage(),
        sizes={'foto':(300,300)}
    ),

    OrderableReferenceField(
        name='contact',
        vocabulary_display_path_bound="-1",
        widget=OrderableReferenceWidget(
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson',),
        multiValued=1,
        relationship='mrevent_contact'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MREvent_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
class IMREvent(Interface):
    pass
##/code-section after-schema

class MREvent(OrderedBaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(OrderedBaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'MREvent'

    meta_type = 'MREvent'
    portal_type = 'MREvent'
    allowed_content_types = ['AgendaItem', 'File']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'MREvent.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "MREvent"
    typeDescMsgId = 'description_edit_mrevent'

    _at_rename_after_creation = True

    schema = MREvent_schema

    ##code-section class-header #fill in your manual code here
    implements(IMREvent)
    ##/code-section class-header

    # Methods


registerType(MREvent, PROJECTNAME)
# end of class MREvent

##code-section module-footer #fill in your manual code here
##/code-section module-footer



