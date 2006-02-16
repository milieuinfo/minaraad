# File: AnnualReport.py
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

from Products.minaraad.content.NewsLetter import NewsLetter
from Products.minaraad.PostMixin import PostMixin


from Products.minaraad.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

AnnualReport_schema = BaseSchema.copy() + \
    getattr(NewsLetter,'schema',Schema(())).copy() + \
    getattr(PostMixin,'schema',Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class AnnualReport(NewsLetter,PostMixin,BaseContent):
    security = ClassSecurityInfo()
    __implements__ = (getattr(NewsLetter,'__implements__',()),) + (getattr(PostMixin,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name = 'AnnualReport'

    meta_type = 'AnnualReport'
    portal_type = 'AnnualReport'
    allowed_content_types = [] + list(getattr(NewsLetter, 'allowed_content_types', [])) + list(getattr(PostMixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    allow_discussion = False
    #content_icon = 'AnnualReport.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "AnnualReport"
    typeDescMsgId = 'description_edit_annualreport'

    _at_rename_after_creation = True

    schema = AnnualReport_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # Methods

registerType(AnnualReport,PROJECTNAME)
# end of class AnnualReport

##code-section module-footer #fill in your manual code here
##/code-section module-footer



