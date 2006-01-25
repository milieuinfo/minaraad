# File: Advisory.py
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
from Products.minaraad.PostMixin import PostMixin


from Products.minaraad.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema=Schema((
    DateTimeField('date',
        widget=CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            description_msgid='minaraad_help_date',
            i18n_domain='minaraad',
        )
    ),

    StringField('policy',
        widget=SelectionWidget(
            label='Policy',
            label_msgid='minaraad_label_policy',
            description_msgid='minaraad_help_policy',
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

Advisory_schema = BaseSchema + \
    getattr(MinaBundle,'schema',Schema(())) + \
    getattr(PostMixin,'schema',Schema(())) + \
    schema

##code-section after-schema #fill in your manual code here
Advisory_schema['description'].isMetadata = False
##/code-section after-schema

class Advisory(MinaBundle,PostMixin,BaseContent):
    """
    An advisory
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(MinaBundle,'__implements__',()),) + (getattr(PostMixin,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Advisory'

    meta_type                  = 'Advisory'
    portal_type                = 'Advisory'
    allowed_content_types      = [] + list(getattr(MinaBundle, 'allowed_content_types', [])) + list(getattr(PostMixin, 'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'Advisory.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    suppl_views                = ()
    typeDescription            = "Advisory"
    typeDescMsgId              = 'description_edit_advisory'

    _at_rename_after_creation  = True

    schema = Advisory_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

registerType(Advisory,PROJECTNAME)
# end of class Advisory

##code-section module-footer #fill in your manual code here
##/code-section module-footer



