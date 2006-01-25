# File: Presentation.py
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



from Products.minaraad.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema=Schema((
    StringField('speaker',
        widget=StringWidget(
            label='Speaker',
            label_msgid='minaraad_label_speaker',
            description_msgid='minaraad_help_speaker',
            i18n_domain='minaraad',
        )
    ),

    StringField('summary',
        widget=StringWidget(
            label='Summary',
            label_msgid='minaraad_label_summary',
            description_msgid='minaraad_help_summary',
            i18n_domain='minaraad',
        )
    ),

    IntegerField('starthour',
        widget=SelectionWidget(
            label='Starthour',
            label_msgid='minaraad_label_starthour',
            description_msgid='minaraad_help_starthour',
            i18n_domain='minaraad',
        ),
        vocabulary=[7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    ),

    IntegerField('startminutes',
        widget=IntegerWidget(
            label='Startminutes',
            label_msgid='minaraad_label_startminutes',
            description_msgid='minaraad_help_startminutes',
            i18n_domain='minaraad',
        )
    ),

    IntegerField('endhour',
        widget=SelectionWidget(
            label='Endhour',
            label_msgid='minaraad_label_endhour',
            description_msgid='minaraad_help_endhour',
            i18n_domain='minaraad',
        ),
        vocabulary=[7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    ),

    IntegerField('endminutes',
        widget=IntegerWidget(
            label='Endminutes',
            label_msgid='minaraad_label_endminutes',
            description_msgid='minaraad_help_endminutes',
            i18n_domain='minaraad',
        )
    ),

    FileField('attachment',
        widget=FileWidget(
            label='Attachment',
            label_msgid='minaraad_label_attachment',
            description_msgid='minaraad_help_attachment',
            i18n_domain='minaraad',
        ),
        storage=AttributeStorage(),
        multiValued=True
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Presentation_schema = BaseSchema + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Presentation(BaseContent):
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Presentation'

    meta_type                  = 'Presentation'
    portal_type                = 'Presentation'
    allowed_content_types      = []
    filter_content_types       = 0
    global_allow               = 0
    allow_discussion           = 0
    #content_icon               = 'Presentation.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    suppl_views                = ()
    typeDescription            = "Presentation"
    typeDescMsgId              = 'description_edit_presentation'

    _at_rename_after_creation  = True

    schema = Presentation_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

registerType(Presentation,PROJECTNAME)
# end of class Presentation

##code-section module-footer #fill in your manual code here
##/code-section module-footer



