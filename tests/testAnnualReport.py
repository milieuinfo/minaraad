# -*- coding: utf-8 -*-
#
# File: testAnnualReport.py
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
# Test-cases for class(es) AnnualReport
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.AnnualReport import AnnualReport

##code-section module-beforeclass #fill in your manual code here

TITLE = "title"
DESCRIPTION = "een omschrijving"
HTMLBODY = "<p>HTML Body boodschap</p>"

##/code-section module-beforeclass


class testAnnualReport(MainTestCase):
    """ test-cases for class(es) AnnualReport
    """

    ##code-section class-header_testAnnualReport #fill in your manual code here
    ##/code-section class-header_testAnnualReport

    def afterSetUp(self):
        """
        """
        self.setRoles(['Manager'])
        self.portal.jaarverslag.invokeFactory('AnnualReport',id='testar')
        self.testar = self.portal.jaarverslag.testar

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

        pass
    # from class AnnualReport:
    # from class AnnualReport:

    def test_email_out(self):
        pass

    # from class AnnualReport:
    def test_export_subscribers(self):
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

    def test_subscribers_export(self):
        pass

    def testAnnualReport(self):
        """ Test if the AnnualReport is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('AnnualReport' in types_)

    def testProperties(self):
        """ Test if the AnnualReport has the correct properties
        """

        self.testar.setTitle(TITLE)
        self.testar.setDescription(DESCRIPTION)
        self.testar.setBody(HTMLBODY,text_format="text/html")
        self.testar.setContact(self.contactperson.UID())

        self.failUnless(self.testar.Title()==TITLE,
                         'Value is %s' % self.testar.Title())
        self.failUnless(self.testar.getDescription()==DESCRIPTION,
                         'Value is %s' % self.testar.getDescription())
        self.failUnless(self.testar.getBody()==HTMLBODY,
                         'Value is %s' % self.testar.getBody())
        self.failUnless(self.testar.getContact()==[self.contactperson],
                         'Value is %s' % self.testar.getContact())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testAnnualReport))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


