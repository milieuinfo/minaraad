# File: MinaBundle.py
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
from EmailMixin import EmailMixin
from Products.ATContentTypes.content.document import ATDocument


from Products.minaraad.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema=Schema((
    TextField('plaintext',
        widget=TextAreaWidget(
            label='Plaintext',
            label_msgid='minaraad_label_plaintext',
            description_msgid='minaraad_help_plaintext',
            i18n_domain='minaraad',
        )
    ),


    ReferenceField('contactpersons',
        widget=ReferenceWidget(
            label='Contactpersons',
            label_msgid='minaraad_label_contactpersons',
            description_msgid='minaraad_help_contactpersons',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson',),
        multiValued=0,
        relationship='minabundles_contactpersons'
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

MinaBundle_schema = getattr(EmailMixin,'schema',Schema(())) + \
    getattr(ATDocument,'schema',Schema(())) + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class MinaBundle(EmailMixin,ATDocument):
    security = ClassSecurityInfo()
    __implements__ = (getattr(EmailMixin,'__implements__',()),) + (getattr(ATDocument,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'MinaBundle'

    meta_type                  = 'MinaBundle'
    portal_type                = 'MinaBundle'
    allowed_content_types      = [] + list(getattr(EmailMixin, 'allowed_content_types', [])) + list(getattr(ATDocument, 'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'MinaBundle.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    suppl_views                = ()
    typeDescription            = "MinaBundle"
    typeDescMsgId              = 'description_edit_minabundle'

    schema = MinaBundle_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

# end of class MinaBundle

##code-section module-footer #fill in your manual code here
##/code-section module-footer



