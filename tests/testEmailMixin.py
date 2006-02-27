# File: testEmailMixin.py
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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Test-cases for class(es) EmailMixin
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.PloneTestCase.PloneTestCase import PloneTestCase

# Import the tested classes
from Products.minaraad.EmailMixin import EmailMixin

##code-section module-beforeclass #fill in your manual code here
from Products.Archetypes.atapi import registerType, BaseContent, BaseSchema
##/code-section module-beforeclass


class testEmailMixin(PloneTestCase):
    """Test-cases for class(es) EmailMixin."""

    ##code-section class-header_testEmailMixin #fill in your manual code here
    ##/code-section class-header_testEmailMixin

    def afterSetUp(self):
        pass

    # from class EmailMixin:
    def test_email(self):
        pass

    # from class EmailMixin:
    def test_getEmailBody(self):
        emailMixin = DummyEmailMixin('blah')
        emailMixin = emailMixin.__of__(self.portal)
        emailMixin.setTitle('Blah')
        emailMixin.setEmailTemplate('<p><span tal:replace="nocall:context/title"/></p>')
        
        email = emailMixin.getEmailBody()
        self.assertEquals(str(email['text/html']).strip(), '<p>Blah</p>')
        self.assertEquals(str(email['text/plain']).strip(), 'Blah')
        
    # Manually created methods


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testEmailMixin))
    return suite

##code-section module-footer #fill in your manual code here
class DummyEmailMixin(EmailMixin, BaseContent):
    """A dummy class that extends EmailMixin.  Using this class is the only
    way to test with Archetypes auto-generated field accessors/mutators."""

    schema = BaseSchema + EmailMixin.schema


registerType(DummyEmailMixin, PROJECTNAME)
##/code-section module-footer

if __name__ == '__main__':
    framework()


