# File: Pressrelease.py
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

Pressrelease_schema = BaseSchema + \
    getattr(MinaBundle,'schema',Schema(())) + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Pressrelease(MinaBundle,BaseContent):
    security = ClassSecurityInfo()
    __implements__ = (getattr(MinaBundle,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Pressrelease'

    meta_type                  = 'Pressrelease'
    portal_type                = 'Pressrelease'
    allowed_content_types      = [] + list(getattr(MinaBundle, 'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'Pressrelease.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    suppl_views                = ()
    typeDescription            = "Pressrelease"
    typeDescMsgId              = 'description_edit_pressrelease'

    _at_rename_after_creation  = True

    schema = Pressrelease_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

registerType(Pressrelease,PROJECTNAME)
# end of class Pressrelease

##code-section module-footer #fill in your manual code here
##/code-section module-footer



