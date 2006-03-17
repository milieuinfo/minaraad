# -*- coding: utf-8 -*-
#
# File: testNewsLetter.py
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
# Test-cases for class(es) NewsLetter
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.NewsLetter import NewsLetter

##code-section module-beforeclass #fill in your manual code here
from DateTime import DateTime
from StructuredText.StructuredText import HTML

TITLE = "title"
DESCRIPTION = "my description"
DATE = DateTime()
HTMLBODY = "<p>blablabla blablabla bladibladi bla</p>"
PLAINBODY = "blablabla blablabla bladibladi bla"
##/code-section module-beforeclass


class testNewsLetter(MainTestCase):
    """ test-cases for class(es) NewsLetter
    """

    ##code-section class-header_testNewsLetter #fill in your manual code here
    ##/code-section class-header_testNewsLetter

    def afterSetUp(self):
        """
        """

        self.setRoles(['Manager'])
        self.portal.nieuwsbrieven.newsl_2006.invokeFactory('NewsLetter', id='testnewsletter')
        self.testnewsletter = self.portal.nieuwsbrieven.newsl_2006.testnewsletter
        
        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Joris')
        self.contactperson = self.portal.contactpersonen.Joris

    # from class NewsLetter:
    def test_email_out(self):
        pass

    # from class EmailMixin:
    def test_email(self):
        """
        """
        #Uncomment one of the following lines as needed
    # from class EmailMixin:
    def test_getEmailBody(self):
        pass

    # from class EmailMixin:
    def test_getSubscriptionId(self):
        pass

    # Manually created methods

    def test_getEmailContentsFromContent(self):
        pass

    def test_getEmailContents(self):
        pass

    def testNewsLetter(self):
        """ Test if the Newsletter is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('NewsLetter' in types_)

    def test_subscribers_export(self):
        pass

    def testProperties(self):
        """ Test if the Newsletter has the correct properties
        """

        self.testnewsletter.setTitle(TITLE)
        self.testnewsletter.setDescription(DESCRIPTION)
        self.testnewsletter.setDate(DATE)
        self.testnewsletter.setBody(HTMLBODY,text_format="text/html")
        self.testnewsletter.setContact(self.contactperson.UID())

        self.failUnless(self.testnewsletter.Title()==TITLE, 
                        'Value is %s' % self.testnewsletter.Title())
        self.failUnless(self.testnewsletter.getDescription()==DESCRIPTION, 
                        'Value is %s' % self.testnewsletter.getDescription())
        self.failUnless(self.testnewsletter.getDate()==DATE, 
                        'Value is %s' % self.testnewsletter.getDate())
        self.failUnless(self.testnewsletter.getBody()==HTMLBODY, 
                        'Value %s is not %s' % (self.testnewsletter.getBody(),HTMLBODY))
        self.failUnless(self.testnewsletter.getContact()==[self.contactperson], 
                        'Value %s is not %s' % (self.testnewsletter.getContact(),self.contactperson))
        
        self.testnewsletter.setBody(PLAINBODY,text_format="text/plain")
        self.failUnless(self.testnewsletter.getBody()==HTMLBODY, 
                        'Value %s is not %s' % (self.testnewsletter.getBody(),HTMLBODY))
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testNewsLetter))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


