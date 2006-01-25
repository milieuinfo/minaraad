# File: PostMixin.py
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
),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PostMixin_schema = BaseSchema + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PostMixin:
    security = ClassSecurityInfo()
    __implements__ = ()


    # This name appears in the 'add' box
    archetype_name             = 'PostMixin'

    meta_type                  = 'PostMixin'
    portal_type                = 'PostMixin'
    allowed_content_types      = []
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'PostMixin.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    suppl_views                = ()
    typeDescription            = "PostMixin"
    typeDescMsgId              = 'description_edit_postmixin'

    schema = PostMixin_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

# end of class PostMixin

##code-section module-footer #fill in your manual code here
##/code-section module-footer



