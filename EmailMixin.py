# File: EmailMixin.py
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

# additional imports from tagged value 'import'
from Products.TemplateFields import ZPTField

##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema = Schema((

    TextField(
        name='plaintext',
        widget=TextAreaWidget(
            label='Plaintext',
            label_msgid='minaraad_label_plaintext',
            i18n_domain='minaraad',
        )
    ),

    ZPTField(
        name='emailTemplate',
    
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

EmailMixin_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class EmailMixin:
    security = ClassSecurityInfo()

    allowed_content_types = []
    schema = EmailMixin_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('email')
    def email(self,addresses):
        """
        
        """
        pass
    security.declarePublic('getEmailBody')
    def getEmailBody(self):
        """
        
        """
        
        cooked = self.getEmailTemplate()
        portal_transforms = getToolByName(self, 'portal_transforms')
        plain = portal_transforms.convertTo('text/plain', cooked)
        
        body = {
            'text/html': cooked,
            'text/plain': plain,
        }
        
        return body

# end of class EmailMixin

##code-section module-footer #fill in your manual code here
##/code-section module-footer



