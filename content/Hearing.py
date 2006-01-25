# File: Hearing.py
# 
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.0-final 
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Rocky Burt <r.burt@zestsoftware.nl>'''
__docformat__ = 'plaintext'


from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.minaraad.MinaBundle import MinaBundle


from Products.minaraad.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema=Schema((
    StringField('subheader',
        widget=StringWidget(
            label='Subheader',
            label_msgid='minaraad_label_subheader',
            description_msgid='minaraad_help_subheader',
            i18n_domain='minaraad',
        )
    ),

    TextField('goal',
        widget=TextAreaWidget(
            label='Goal',
            label_msgid='minaraad_label_goal',
            description_msgid='minaraad_help_goal',
            i18n_domain='minaraad',
        )
    ),

    StringField('location',
        widget=StringWidget(
            label='Location',
            label_msgid='minaraad_label_location',
            description_msgid='minaraad_help_location',
            i18n_domain='minaraad',
        )
    ),

    DateTimeField('start',
        widget=CalendarWidget(
            label='Start',
            label_msgid='minaraad_label_start',
            description_msgid='minaraad_help_start',
            i18n_domain='minaraad',
        )
    ),

    DateTimeField('end',
        widget=CalendarWidget(
            label='End',
            label_msgid='minaraad_label_end',
            description_msgid='minaraad_help_end',
            i18n_domain='minaraad',
        )
    ),

    StringField('themes',
        widget=SelectionWidget(
            label='Themes',
            label_msgid='minaraad_label_themes',
            description_msgid='minaraad_help_themes',
            i18n_domain='minaraad',
        )
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Hearing_schema = BaseFolderSchema + \
    getattr(MinaBundle,'schema',Schema(())) + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Hearing(MinaBundle,BaseFolder):
    security = ClassSecurityInfo()
    __implements__ = (getattr(MinaBundle,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Hearing'

    meta_type                  = 'Hearing'
    portal_type                = 'Hearing'
    allowed_content_types      = ['Presentation'] + list(getattr(MinaBundle, 'allowed_content_types', []))
    filter_content_types       = 1
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'Hearing.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    suppl_views                = ()
    typeDescription            = "Hearing"
    typeDescMsgId              = 'description_edit_hearing'

    _at_rename_after_creation  = True

    schema = Hearing_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

registerType(Hearing,PROJECTNAME)
# end of class Hearing

##code-section module-footer #fill in your manual code here
##/code-section module-footer



